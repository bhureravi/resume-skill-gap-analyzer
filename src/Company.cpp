#include <iostream>
#include <fstream>
#include "../include/Company.h"
using namespace std;

Company::Company() {
    companyName = "";
}

Company::Company(string name) {
    companyName = name;
}

void Company::setCompanyName(string name) {
    companyName = name;
}

string Company::getCompanyName() {
    return companyName;
}

void Company::setExpectedSkills(vector<string> skills) {
    expectedSkills = skills;
}

vector<string> Company::getExpectedSkills() {
    return expectedSkills;
}

void Company::setFocusAreas(vector<string> areas) {
    focusAreas = areas;
}

vector<string> Company::getFocusAreas() {
    return focusAreas;
}

void Company::setPrepTips(vector<string> tips) {
    prepTips = tips;
}

vector<string> Company::getPrepTips() {
    return prepTips;
}

bool Company::loadFromFile(string filename) {
    ifstream file(filename);

    if (!file.is_open()) {
        cout << "Error: Could not open company file.\n";
        return false;
    }

    expectedSkills.clear();
    focusAreas.clear();
    prepTips.clear();

    string line;
    bool readingExpected = false;
    bool readingFocus = false;
    bool readingTips = false;

    if (getline(file, line)) {
        companyName = line;
    }

    while (getline(file, line)) {
        if (line == "Expected:") {
            readingExpected = true;
            readingFocus = false;
            readingTips = false;
            continue;
        }

        if (line == "Focus:") {
            readingExpected = false;
            readingFocus = true;
            readingTips = false;
            continue;
        }

        if (line == "Tips:") {
            readingExpected = false;
            readingFocus = false;
            readingTips = true;
            continue;
        }

        if (line != "") {
            if (readingExpected) {
                expectedSkills.push_back(line);
            } else if (readingFocus) {
                focusAreas.push_back(line);
            } else if (readingTips) {
                prepTips.push_back(line);
            }
        }
    }

    file.close();
    cout << "Company loaded successfully from file.\n";
    return true;
}

void Company::displayCompany() {
    cout << "\n----- Selected Company -----\n";
    cout << "Company Name: " << companyName << endl;

    cout << "Expected Skills:\n";
    for (string skill : expectedSkills) {
        cout << "- " << skill << endl;
    }

    cout << "Focus Areas:\n";
    for (string area : focusAreas) {
        cout << "- " << area << endl;
    }

    cout << "Prep Tips:\n";
    for (string tip : prepTips) {
        cout << "- " << tip << endl;
    }

    cout << "----------------------------\n";
}