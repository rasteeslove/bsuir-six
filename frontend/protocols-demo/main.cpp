#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <sstream>

// So this is both client and server I guess
// Command line arguments: only one, being the username

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

void text(std::string me, std::string they) {
	// checking if they exist ?
	// making tcp connection ?
	// if they are not online then return ?
	// otherwise tell them that you are texting ?

	// getting message:
	std::cout << "Enter the message: ";

	// sending w udp ?
}

int main(int argc, char *argv[]) {
	if (argc != 2) {
		std::cout << "Invalid command line arguments!\n";
		return -1;
	}

	std::string username(argv[1]);

	// logging in?
	// adding username to file ?

	std::cout << "Welcome!\n";
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

		if (std::find(command_options.begin(), command_options.end(), command_words[0]) != command_options.end()) {
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
		} else {
			std::cout << "Invalid command!\n";
		}

	}
	return 0;
}

