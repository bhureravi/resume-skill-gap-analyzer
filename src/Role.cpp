#include <iostream>
#include <fstream>
#include "../include/Role.h"
using namespace std;

Role::Role() {
    roleName = "";
}

Role::Role(string name) {
    roleName = name;
}

void Role::setRoleName(string name) {
    roleName = name;
}

string Role::getRoleName() {
    return roleName;
}

void Role::setRequiredSkills(vector<string> skills) {
    requiredSkills = skills;
}

vector<string> Role::getRequiredSkills() {
    return requiredSkills;
}

void Role::setPreferredSkills(vector<string> skills) {
    preferredSkills = skills;
}

vector<string> Role::getPreferredSkills() {
    return preferredSkills;
}

bool Role::loadFromFile(string filename) {
    ifstream file(filename);

    if (!file.is_open()) {
        cout << "Error: Could not open role file.\n";
        return false;
    }

    requiredSkills.clear();
    preferredSkills.clear();

    string line;
    bool readingRequired = false;
    bool readingPreferred = false;

    if (getline(file, line)) {
        roleName = line;
    }

    while (getline(file, line)) {
        if (line == "Required:") {
            readingRequired = true;
            readingPreferred = false;
            continue;
        }

        if (line == "Preferred:") {
            readingRequired = false;
            readingPreferred = true;
            continue;
        }

        if (line != "") {
            if (readingRequired) {
                requiredSkills.push_back(line);
            } else if (readingPreferred) {
                preferredSkills.push_back(line);
            }
        }
    }

    file.close();
    cout << "Role loaded successfully from file.\n";
    return true;
}

void Role::displayRole() {
    cout << "\n----- Selected Role -----\n";
    cout << "Role Name: " << roleName << endl;

    cout << "Required Skills:\n";
    for (string skill : requiredSkills) {
        cout << "- " << skill << endl;
    }

    cout << "Preferred Skills:\n";
    for (string skill : preferredSkills) {
        cout << "- " << skill << endl;
    }

    cout << "-------------------------\n";
}