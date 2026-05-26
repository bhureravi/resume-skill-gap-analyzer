#include <iostream>
#include <fstream>
#include <algorithm>
#include <sstream>
#include "../include/SkillExtractor.h"
using namespace std;

string SkillExtractor::toLowerCase(string text) {
    string result = text;
    transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

string SkillExtractor::removeExtraSymbols(string text) {
    string result = "";
    for (char ch : text) {
        if (isalnum(ch) || ch == ' ' || ch == '+') {
            result += ch;
        } else {
            result += ' ';
        }
    }
    return result;
}

vector<string> SkillExtractor::loadSkillsFromFile(string filename) {
    vector<string> skills;
    ifstream file(filename);

    if (!file.is_open()) {
        cout << "Error: Could not open skills file.\n";
        return skills;
    }

    string line;
    while (getline(file, line)) {
        if (line != "") {
            skills.push_back(line);
        }
    }

    file.close();
    return skills;
}

vector<string> SkillExtractor::extractSkills(string text, vector<string> skillDatabase) {
    vector<string> foundSkills;

    text = removeExtraSymbols(text);
    string lowerText = toLowerCase(text);

    for (string skill : skillDatabase) {
        string lowerSkill = toLowerCase(skill);

        if (lowerText.find(lowerSkill) != string::npos) {
            foundSkills.push_back(skill);
        }
    }

    return foundSkills;
}