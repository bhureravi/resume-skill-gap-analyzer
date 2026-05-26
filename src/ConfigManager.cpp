#include <iostream>
#include <fstream>
#include <sstream>
#include "../include/ConfigManager.h"
using namespace std;

bool ConfigManager::loadConfig(string filename) {
    ifstream file(filename);

    if (!file.is_open()) {
        cout << "Error: Could not open config file.\n";
        return false;
    }

    configData.clear();

    string line;
    while (getline(file, line)) {
        if (line == "") {
            continue;
        }

        size_t pos = line.find('=');
        if (pos != string::npos) {
            string key = line.substr(0, pos);
            string value = line.substr(pos + 1);
            configData[key] = value;
        }
    }

    file.close();
    return true;
}

string ConfigManager::getValue(string key) {
    if (configData.find(key) != configData.end()) {
        return configData[key];
    }
    return "";
}

void ConfigManager::displayConfig() {
    cout << "\n----- Config Values -----\n";
    for (auto pair : configData) {
        cout << pair.first << " = " << pair.second << endl;
    }
    cout << "-------------------------\n";
}