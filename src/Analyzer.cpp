#include <iostream>
#include <unordered_set>
#include "../include/Analyzer.h"
using namespace std;

Analyzer::Analyzer() {
    roleMatchScore = 0;
    companyMatchScore = 0;
    overallScore = 0;
}

void Analyzer::analyze(Resume resume, Role role, Company company) {
    missingRoleSkills.clear();
    missingCompanySkills.clear();
    roleMatchScore = 0;
    companyMatchScore = 0;
    overallScore = 0;

    vector<string> resumeSkills = resume.getExtractedSkills();
    vector<string> requiredSkills = role.getRequiredSkills();
    vector<string> companySkills = company.getExpectedSkills();

    unordered_set<string> resumeSkillSet;

    for (string skill : resumeSkills) {
        resumeSkillSet.insert(skill);
    }

    int roleMatched = 0;
    for (string skill : requiredSkills) {
        if (resumeSkillSet.find(skill) != resumeSkillSet.end()) {
            roleMatched++;
        } else {
            missingRoleSkills.push_back(skill);
        }
    }

    int companyMatched = 0;
    for (string skill : companySkills) {
        if (resumeSkillSet.find(skill) != resumeSkillSet.end()) {
            companyMatched++;
        } else {
            missingCompanySkills.push_back(skill);
        }
    }

    if (requiredSkills.size() > 0) {
        roleMatchScore = (roleMatched * 100) / requiredSkills.size();
    }

    if (companySkills.size() > 0) {
        companyMatchScore = (companyMatched * 100) / companySkills.size();
    }

    overallScore = (roleMatchScore * 70 + companyMatchScore * 30) / 100;
}

int Analyzer::getRoleMatchScore() {
    return roleMatchScore;
}

int Analyzer::getCompanyMatchScore() {
    return companyMatchScore;
}

int Analyzer::getOverallScore() {
    return overallScore;
}

vector<string> Analyzer::getMissingRoleSkills() {
    return missingRoleSkills;
}

vector<string> Analyzer::getMissingCompanySkills() {
    return missingCompanySkills;
}

void Analyzer::displayAnalysis() {
    cout << "\n----- Analysis Result -----\n";
    cout << "Role Match Score: " << roleMatchScore << "%\n";
    cout << "Company Match Score: " << companyMatchScore << "%\n";
    cout << "Overall Score: " << overallScore << "%\n";

    cout << "\nMissing Role Skills:\n";
    if (missingRoleSkills.empty()) {
        cout << "None\n";
    } else {
        for (string skill : missingRoleSkills) {
            cout << "- " << skill << endl;
        }
    }

    cout << "\nMissing Company Skills:\n";
    if (missingCompanySkills.empty()) {
        cout << "None\n";
    } else {
        for (string skill : missingCompanySkills) {
            cout << "- " << skill << endl;
        }
    }

    cout << "---------------------------\n";
}