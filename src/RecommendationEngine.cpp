#include <iostream>
#include <algorithm>
#include "../include/RecommendationEngine.h"
using namespace std;

RecommendationEngine::RecommendationEngine() {
    recommendations.clear();
}

string RecommendationEngine::toLowerCase(string text) {
    string result = text;
    transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

bool RecommendationEngine::isHighPrioritySkill(string skill) {
    string s = toLowerCase(skill);

    if (s == "c++" || s == "dsa" || s == "oop" || s == "stl" ||
        s == "git" || s == "sql" || s == "system design" ||
        s == "rest api" || s == "problem solving" || s == "python") {
        return true;
    }

    return false;
}

bool RecommendationEngine::alreadyAdded(string item, vector<string> items) {
    for (string x : items) {
        if (x == item) {
            return true;
        }
    }
    return false;
}

vector<string> RecommendationEngine::generateRecommendations(Resume resume, Role role, Company company, Analyzer analyzer) {
    recommendations.clear();

    vector<string> missingRoleSkills = analyzer.getMissingRoleSkills();
    vector<string> missingCompanySkills = analyzer.getMissingCompanySkills();
    vector<string> rolePreferredSkills = role.getPreferredSkills();
    vector<string> companyTips = company.getPrepTips();
    vector<string> companyFocus = company.getFocusAreas();
    vector<string> resumeSkills = resume.getExtractedSkills();

    if (analyzer.getOverallScore() < 40) {
        recommendations.push_back("Focus first on core fundamentals: C++, OOP, DSA, and STL.");
    } else if (analyzer.getOverallScore() < 70) {
        recommendations.push_back("You have a decent base. Improve missing role and company skills next.");
    } else {
        recommendations.push_back("You are close to being ready. Focus on revision, mock interviews, and projects.");
    }

    for (string skill : missingRoleSkills) {
        string tip = "Priority skill for role: " + skill;
        if (!alreadyAdded(tip, recommendations)) {
            if (isHighPrioritySkill(skill)) {
                recommendations.push_back(tip);
            }
        }
    }

    for (string skill : missingCompanySkills) {
        string tip = "Company expectation to cover: " + skill;
        if (!alreadyAdded(tip, recommendations)) {
            if (isHighPrioritySkill(skill)) {
                recommendations.push_back(tip);
            }
        }
    }

    for (string skill : rolePreferredSkills) {
        bool found = false;
        for (string rs : resumeSkills) {
            if (toLowerCase(rs) == toLowerCase(skill)) {
                found = true;
                break;
            }
        }

        if (!found) {
            string tip = "Good-to-have skill for this role: " + skill;
            if (!alreadyAdded(tip, recommendations)) {
                recommendations.push_back(tip);
            }
        }
    }

    for (string focus : companyFocus) {
        string tip = "Company focus area: " + focus;
        if (!alreadyAdded(tip, recommendations)) {
            recommendations.push_back(tip);
        }
    }

    for (string tip : companyTips) {
        string finalTip = "Prep tip: " + tip;
        if (!alreadyAdded(finalTip, recommendations)) {
            recommendations.push_back(finalTip);
        }
    }

    if (recommendations.size() > 8) {
        recommendations.resize(8);
    }

    return recommendations;
}

void RecommendationEngine::displayRecommendations() {
    cout << "\n----- Recommendations -----\n";

    if (recommendations.empty()) {
        cout << "No recommendations generated yet.\n";
        cout << "First run the analysis.\n";
        cout << "---------------------------\n";
        return;
    }

    for (int i = 0; i < recommendations.size(); i++) {
        cout << i + 1 << ". " << recommendations[i] << endl;
    }

    cout << "---------------------------\n";
}