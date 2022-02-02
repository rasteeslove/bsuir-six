#include <iostream>
#include <fstream>
#include <string.h>
#include <vector>

/*
Cypher docu:

A CLI tool. It accepts 5+2n arguments (n >= 0, integer):
	1) 0 | 1 | 2| 3, which corresponds to:
		0 => Caesar Encrypt,
		1 => Caesar Decrypt,
		2 => Vigenere Encrypt,
		3 => Vigenere Decrypt;
	2) path to the file to translate (should exist);
	3) path to the file to write (should not exist);
	4) valid encryption/decryption key;
	5) the ASCII character range bounds for the previous argument key (e.g. "az");
	...) more 4&5 argument pairs if desired;
Behavior on out-of-range chars: ignore.

In case of Caesar: multiple bounds | key&bounds, e.g.:
	"cy 0 s.txt t.txt 13 az AZ" | "cy 0 s.txt t.txt 13 az 13 AZ",
	"cy 1 e.txt d.txt 7 az AZ" | "cy 1 e.txt d.txt 7 az 7 AZ",
In case of Vigenere: multiple key&bounds pairs, e.g.:
	"cy 2 s.txt t.txt secretkey az SECRETKEY AZ";
	(the "i" char counter in the second for loop of the translate_file function
	 is common for all of the keybounds pairs)
*/

std::vector<std::pair<std::string, std::string>> keybounds;

bool file_exists(std::string path) {
	std::ifstream is(path);
	bool result = is.good();
	is.close();

	return result;
}

void translate_file(std::string source_path, std::string target_path, int mode) {
	std::ifstream is(source_path);
	std::ofstream os(target_path);

	std::vector<int> alphabet_sizes;
	for (int i = 0; i < keybounds.size(); i++)
		alphabet_sizes.push_back(keybounds[i].second[1] - keybounds[i].second[0] + 1);

	char c;
	int sign = (mode == 0 || mode == 2 ? 1 : -1);
	for (long i = 0; is.get(c);) {
		char cc = c;

		// char #i translation:
		for (int j = 0; j < keybounds.size(); j++) {
			std::string bounds = keybounds[j].second;
			if (cc >= bounds[0] && cc <= bounds[1]) {
				std::string key = keybounds[j].first;
				int shift = (mode == 0 || mode == 1 ? std::stoi(key) : int(key[i % key.length()] - bounds[0]));
				cc = bounds[0] + (alphabet_sizes[j] + cc - bounds[0] + sign * shift) % alphabet_sizes[j];
				i++;
				break;
			}
		}

		os.put(cc);
	}

	is.close();
	os.close();
}

int main(int argc, char* argv[]) {
	if (argc < 6 || argc % 2 != 0) {
		std::cout << "Wrong arguments! *docu could be here*";
		return -1;
	}

	// Files:
	std::string source_path(argv[2]);
	std::string target_path(argv[3]);

	// Encryption/decryption keys and bounds:
	for (int i = 4; i < argc; i += 2) {
		std::pair<std::string, std::string> pair(argv[i], argv[i+1]);
		keybounds.push_back(pair);
	}

	// Validating the arguments. These conditions are to be ensured:
	// 1) the mode is valid;
	// 2) all bounds are valid;
	// 3) all keys are valid for the selected mode and the corresponding bounds;
	// 4) the source file exists;
	// 5) the target file does not exist;

	// 1:
	int mode;
	try {
		mode = std::stoi(argv[1]);
	} catch (...) {
		std::cout << "Invalid mode!\n";
		return -1;
	}
	if (mode != 0 && mode != 1 && mode != 2 && mode != 3) {
		std::cout << "Invalid mode!\n";
		return -1;
	}

	// 2&3: checking if all the bounds and their keys are valid:
	for (int i = 0; i < keybounds.size(); i++) {
		std::string key = keybounds[i].first;
		std::string bounds = keybounds[i].second;

		// 2:
		if (bounds.length() != 2 || bounds[0] > bounds[1]) {
			std::cout << "Invalid ASCII char bounds!\n";
			return -1;
		}

		// 3:
		// (not checking the length of key because it's not zero
		// since it's detected as a command line argument)
		if (mode == 0 || mode == 1) {
			int shift;
			try {
				shift = std::stoi(key);
			} catch (...) {
				std::cout << "Invalid translation key!\n";
				return -1;
			}
			if (shift < 0) {
				std::cout << "Invalid translation key!\n";
				return -1;
			}
			shift %= (bounds[1] - bounds[0] + 1);
			key = std::to_string(shift);
		} else
			for (int i = 0; i < key.length(); i++)
				if (key[i] < bounds[0] || key[i] > bounds[1]) {
					std::cout << "Invalid translation key!\n";
					return -1;
		}
	}

	// 4:
	if (!file_exists(source_path)) {
		std::cout << "Source file does not exist!\n";
		return -1;
	}

	// 5:
	if (file_exists(target_path)) {
		std::cout << "Target file already exists!\n";
		return -1;
	}

	// Informing the user of the actions to be performed:
	std::cout << "Info:\n";
	std::cout << "> Translating \"" << source_path << "\" file contents into \"" << target_path << "\" file.\n";
	std::cout << "> The translation method is \"" << (mode == 0 ? "Caesar Encrypt" :
                                                         (mode == 1 ? "Caesar Decrypt" :
                                                         (mode == 2 ? "Vigenere Encrypt" :
                                                         (mode == 3 ? "Vigenere Decrypt" :
                                                          "ERROR!")))) << "\".\n";
	std::cout << "> The encryption/decryption key&bounds pairs are:\n";
	for (int i = 0; i < keybounds.size(); i++) {
		std::cout << "\t[" << keybounds[i].first << ", " << keybounds[i].second << "]\n";
	}
	std::cout << "> The characters of the source file not included in any of the specified bounds are to be translated into the target file as they are.\n";

	std::cout << "\n";

	// Asking the user whether to continue:
	std::string choice = "";
	do {
		std::cout << "Do you wish to continue? [y/n]: ";
		std::cin >> choice;
	} while (choice != "y" && choice != "n");

	if (choice == "n")
		return -1;

	// Doing the thing:
	try {
		translate_file(source_path, target_path, mode);
	} catch (...) {
		std::cout << "An error occured while translating!\n";
		return -1;
	}

	std::cout << "Success!\n";
	return 0;
}
