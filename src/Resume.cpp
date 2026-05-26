#include <iostream>
#include <fstream>
#include <sstream>
#include "../include/Resume.h"
using namespace std;

Resume::Resume() {
    rawText = "";
}

void Resume::setRawText(string text) {
    rawText = text;
}

string Resume::getRawText() {
    return rawText;
}

void Resume::setExtractedSkills(vector<string> skills) {
    extractedSkills = skills;
}

vector<string> Resume::getExtractedSkills() {
    return extractedSkills;
}

bool Resume::loadFromFile(string filename) {
    ifstream file(filename);

    if (!file.is_open()) {
        cout << "Error: Could not open resume file.\n";
        return false;
    }

    stringstream buffer;
    string line;

    while (getline(file, line)) {
        buffer << line << "\n";
    }

    rawText = buffer.str();
    file.close();

    cout << "Resume loaded successfully from file.\n";
    return true;
}

void Resume::displayResume() {
    cout << "\n----- Resume Content -----\n";
    cout << rawText << endl;
    cout << "--------------------------\n";
}