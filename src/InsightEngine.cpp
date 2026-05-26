#include <iostream>
#include <algorithm>
#include "../include/InsightEngine.h"
using namespace std;

InsightEngine::InsightEngine() {
    readinessLevel = "Not analyzed yet";
    topPriorities.clear();
}

string InsightEngine::toLowerCase(string text) {
    string result = text;
    transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

bool InsightEngine::alreadyAdded(string item, vector<string> items) {
    for (string x : items) {
        if (x == item) {
            return true;
        }
    }
    return false;
}

void InsightEngine::buildInsights(Resume resume, Role role, Company company, Analyzer analyzer) {
    topPriorities.clear();

    int score = analyzer.getOverallScore();

    if (score < 40) {
        readinessLevel = "Beginner";
    } else if (score < 70) {
        readinessLevel = "Intermediate";
    } else {
        readinessLevel = "Job Ready";
    }

    vector<string> missingRole = analyzer.getMissingRoleSkills();
    vector<string> missingCompany = analyzer.getMissingCompanySkills();

    for (string skill : missingRole) {
        if (topPriorities.size() >= 5) {
            break;
        }

        string item = "Role gap: " + skill;
        if (!alreadyAdded(item, topPriorities)) {
            topPriorities.push_back(item);
        }
    }

    for (string skill : missingCompany) {
        if (topPriorities.size() >= 5) {
            break;
        }

        string item = "Company gap: " + skill;
        if (!alreadyAdded(item, topPriorities)) {
            topPriorities.push_back(item);
        }
    }

    if (topPriorities.empty()) {
        topPriorities.push_back("Your resume already matches the chosen role and company well.");
    }
}

string InsightEngine::getReadinessLevel() {
    return readinessLevel;
}

vector<string> InsightEngine::getTopPriorities() {
    return topPriorities;
}

void InsightEngine::displayInsights() {
    cout << "\n========== INSIGHTS ==========\n";
    cout << "Readiness Level: " << readinessLevel << endl;

    cout << "\nTop Priorities:\n";
    for (string item : topPriorities) {
        cout << "- " << item << endl;
    }

    cout << "==============================\n";
}