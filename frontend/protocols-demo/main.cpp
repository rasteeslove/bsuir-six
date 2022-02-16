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

#define BUFFER_LEN 1024

// So this is both client and server I guess
// Command line arguments: only one, being the username

std::string db_name = "txt_file_lol.txt";
std::string online_db_name = "another_txt_file.txt";
std::vector<std::pair<std::string, std::string>> message_queue;
std::mutex mtx;

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

void text(std::string me, std::string they) {
	int their_port = get_port(they).first;

	// check if they exist:
	if (their_port == -1) {
		std::cout << "No user with this username!\n";
		return;
	}

	// getting message:
	std::cout << "Enter the message (Press ENTER to finish): ";
	std::string message;
	std::getline(std::cin, message);

	message = me + ":" + message + "\n"; // maybe add time

	// making udp connection:
	int udp_sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (udp_sock_fd < 0) {
		std::cout << "Socket creation error!\n";
		return;
	}

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

void listen_for_messages(int my_port) {
	int my_sock_fd;
	char buffer[BUFFER_LEN];
	struct sockaddr_in my_addr;

	my_sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (my_sock_fd < 0) {
		std::cout << "Socket creation error!\n";
	}

	memset(&my_addr, 0, sizeof(my_addr));
	my_addr.sin_family = AF_INET;
	my_addr.sin_addr.s_addr = INADDR_ANY;
	my_addr.sin_port = htons(my_port);

	if (bind(my_sock_fd, (const struct sockaddr *)&my_addr,
			sizeof(my_addr)) < 0) {
		std::cout << "Bind error!\n";
	}

	struct sockaddr_in other_addr;
	memset(&other_addr, 0, sizeof(other_addr));
	int len = sizeof(other_addr);

	while (true) {
		int n = recvfrom(my_sock_fd, (char *)buffer, BUFFER_LEN,
			MSG_WAITALL, (struct sockaddr *) &other_addr,
			(socklen_t *)&len);

		std::string message_to_me = std::string(buffer);

		std::string sender, content;
		std::string* target = &sender;
		for (int i = 0; i < message_to_me.length() && message_to_me[i] != '\n'; i++) {
			if (message_to_me[i] == ':' && target == &sender) {
				target = &content;
			} else {
				*target += message_to_me[i];
			}
		}

		mtx.lock();
		message_queue.push_back(std::pair<std::string, std::string>(sender, content));
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

	std::thread listening(listen_for_messages, my_port);

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
		} else if (command == "") {
			// do nothing lol, to not flood the console
		} else {
			std::cout << "Invalid command!\n";
		}

		// dump all messages now:
		mtx.lock();
		for (int i = 0; i < message_queue.size(); i++) {
			std::cout << message_queue[i].first << " texted you: " << message_queue[i].second << "\n";
		}
		message_queue.clear();
		mtx.unlock();
	}
	return 0;
}
