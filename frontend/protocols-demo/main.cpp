#include <iostream>
#include <string>
#include <string.h>
#include <vector>
#include <algorithm>
#include <sstream>
#include <fstream>

#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include <thread>
#include <mutex>

#include <chrono>
#include <ctime>

#define BUFFER_LEN 1024

// So this is both client and server I guess
// This is a CLI tool, so command line arguments:
//     only one, being the username

// username should only use a-z, A-Z, 0-9, _ characters

// Messages to be transmitted using the following universal protocol:
// "[sender_username]|[receiver_username]|[time_of_departure]|[message_content]\n"

// "[username] [assigned_port]"-pairs to be stored in a text file

// Messages that each user sends and receives to be stored in a file whose name is the user's username
// Format is the same as for sending

// syncing message histories ???
// option 1: creating online users db and allowing to text only if the other side is online

std::string db_name = "txt_file_lol.txt";

std::vector<std::vector<std::string>> message_queue;
std::mutex mtx;

// split a command into words
std::vector<std::string> deconstruct_command(std::string command) {
	std::vector<std::string> words;
	std::cin.clear();
	std::istringstream ss(command);

	std::string tmp;
	while (ss >> tmp) {
		words.push_back(tmp);
	}

	return words;
}

// search for username in db and get their port as the 1st el in pair;
// if not found, return -1 as first, last assigned port number as second;
std::pair<int, int> get_port(std::string username) {
	std::ifstream is;
	is.open(db_name);

	std::string u;
	int p;
	while (is >> u >> p) {
		if (u == username) {
			is.close();
			return std::pair<int, int>(p, 0);
		}
	}

	is.close();
	return std::pair<int, int>(-1, p);
}

// add new user to db: their username and new port;
int new_user_port(std::string username, int last_assigned) {
	int new_port = last_assigned + 1;

	std::ofstream os;
	try {
		os.open(db_name, std::ios_base::app);
		os << "\n" << username << " " << new_port;
	} catch (...) {
		return -1;
	}

	os.close();
	return 0;
}

// function for texting someone
void text(std::string me, std::string they) {
	// search for their port:
	int their_port = get_port(they).first;

	// check if they exist:
	if (their_port == -1) {
		std::cout << "No user with this username!\n";
		return;
	}

	// getting your message:
	std::cout << "Enter the message (Press ENTER to finish): ";
	std::string message;
	std::getline(std::cin, message);

	// forming message string:
	auto now = std::chrono::system_clock::now();
	std::time_t now_time = std::chrono::system_clock::to_time_t(now);
	std::string time_string = std::string(std::ctime(&now_time));
	time_string.erase(std::remove(time_string.begin(), time_string.end(), '\n'), time_string.end());
	message = me + "|" + they + "|" + time_string + "|" + message + "\n";

	// making udp connection:
	int udp_sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (udp_sock_fd < 0) {
		std::cout << "Socket creation error!\n";
		return;
	}

	// filling data:
	struct sockaddr_in their_addr;
	memset(&their_addr, 0, sizeof(their_addr));
	their_addr.sin_family = AF_INET;
    their_addr.sin_port = htons(their_port);
    their_addr.sin_addr.s_addr = INADDR_ANY;

	sendto(udp_sock_fd, message.c_str(), strlen(message.c_str()),
        MSG_CONFIRM, (const struct sockaddr *) &their_addr, 
            sizeof(their_addr));

	close(udp_sock_fd);
}

// parse a message string into sender, receiver, time_string, and content strings
std::vector<std::string> deconstruct_message(std::string message) {
	char separator = '|';

	std::string sender, receiver, time_string, content;
	std::string* target = &sender;
	for (int i = 0; i < message.length() && message[i] != '\n'; i++) {
		if (message[i] == separator && target == &sender) {
			target = &receiver;
		} else if (message[i] == separator && target == &receiver) {
			target = &time_string;
		} else if (message[i] == separator && target == &time_string) {
			target = &content;
		} else {
			*target += message[i];
		}
	}

	return std::vector<std::string>({sender, receiver, time_string, content});
}

// to be running in a separate thread and getting messages for the user
void listen_for_messages(std::string my_username, int my_port) {
	int my_sock_fd;
	char buffer[BUFFER_LEN];
	struct sockaddr_in my_addr;

	// create my socket
	my_sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (my_sock_fd < 0) {
		std::cout << "Socket creation error!\n";
	}

	// fill some data
	memset(&my_addr, 0, sizeof(my_addr));
	my_addr.sin_family = AF_INET;
	my_addr.sin_addr.s_addr = INADDR_ANY;
	my_addr.sin_port = htons(my_port);

	// bind or whatever
	if (bind(my_sock_fd, (const struct sockaddr *)&my_addr, sizeof(my_addr)) < 0) {
		std::cout << "Bind error!\n";
	}

	// I don't get the logic but this thing just works
	struct sockaddr_in other_addr;
	memset(&other_addr, 0, sizeof(other_addr));
	int len = sizeof(other_addr);

	// getting message by message
	while (true) {
		int n = recvfrom(my_sock_fd, (char *)buffer, BUFFER_LEN,
			MSG_WAITALL, (struct sockaddr *) &other_addr,
			(socklen_t *)&len);

		std::string message_to_me = std::string(buffer);

		std::vector<std::string> message_info = deconstruct_message(message_to_me);

		// small sanity check
		if (message_info[1] != my_username) {
			std::cout << "Wow, smth went really wrong!\n";
		}

		// pushing messages to the user's message queue
		mtx.lock();
		message_queue.push_back(message_info);
		mtx.unlock();
	}
	
	close(my_sock_fd);
}

int main(int argc, char *argv[]) {
	if (argc != 2) {
		std::cout << "Invalid command line arguments!\n";
		return -1;
	}

	std::string username(argv[1]);

	// logging in:
	std::pair<int, int> port_info = get_port(username);
	int my_port;
	if (port_info.first == -1) {
		my_port = new_user_port(username, port_info.second);
		if (my_port == -1) {
			std::cout << "User creation error!\n";
			return -1;
		}
		std::cout << "Welcome!\n";
	} else {
		my_port = port_info.first;
		std::cout << "Welcome back!\n";
	}

	std::thread listening(listen_for_messages, username, my_port);

	std::vector<std::string> command_options{ "exit", "text" };
	while (true) {
		std::cout << "Awaiting commands: ";

		// Commands:
		// - exit
		// - text [username]
		// ? history [username]

		std::string command;
		std::getline(std::cin, command);
		std::vector<std::string> command_words = deconstruct_command(command);

		if (command_words.size() != 0 && std::find(command_options.begin(), command_options.end(), command_words[0]) != command_options.end()) {
			if (command_words[0] == "exit") {
				if (command_words.size() == 1) {
					std::cout << "Exiting now!\n";
					return 0;
				} else {
					std::cout << "The exit command does not require arguments!\n";
				}
			} else if (command_words[0] == "text") {
				if (command_words.size() == 2) {
					text(username, command_words[1]);
				} else {
					std::cout << "The text command requires 1 argument!\n";
				}
			}
		} else if (command != "") {
			std::cout << "Invalid command!\n";
		}

		// dump all messages now:
		if (message_queue.size() != 0) {
			std::cout << "New messages:\n";
			mtx.lock();
			for (int i = 0; i < message_queue.size(); i++) {
				std::cout << "\t" << message_queue[i][0] << " at " << message_queue[i][2] << ": " << message_queue[i][3] << "\n";
			}
			message_queue.clear();
			mtx.unlock();
		}
	}
	return 0;
}
