#include <iostream>
#include <fstream>
#include <ctime>
#include "../include/HistoryManager.h"
using namespace std;

void HistoryManager::saveRunToHistory(string filename, Resume resume, Role role, Company company, Analyzer analyzer) {
    ofstream out(filename, ios::app);

    if (!out.is_open()) {
        cout << "Could not open history file.\n";
        return;
    }

    time_t now = time(0);
    char* dt = ctime(&now);

    out << "=====================================\n";
    out << "Run Time: " << dt;
    out << "Role: " << role.getRoleName() << endl;
    out << "Company: " << company.getCompanyName() << endl;
    out << "Role Match Score: " << analyzer.getRoleMatchScore() << "%\n";
    out << "Company Match Score: " << analyzer.getCompanyMatchScore() << "%\n";
    out << "Overall Score: " << analyzer.getOverallScore() << "%\n";

    out << "Missing Role Skills:\n";
    vector<string> missingRole = analyzer.getMissingRoleSkills();
    if (missingRole.empty()) {
        out << "None\n";
    } else {
        for (string skill : missingRole) {
            out << "- " << skill << "\n";
        }
    }

    out << "Missing Company Skills:\n";
    vector<string> missingCompany = analyzer.getMissingCompanySkills();
    if (missingCompany.empty()) {
        out << "None\n";
    } else {
        for (string skill : missingCompany) {
            out << "- " << skill << "\n";
        }
    }

    out << "=====================================\n\n";
    out.close();
}

void HistoryManager::showHistory(string filename) {
    ifstream in(filename);

    if (!in.is_open()) {
        cout << "No history file found yet.\n";
        return;
    }

    cout << "\n========== ANALYSIS HISTORY ==========\n";

    string line;
    while (getline(in, line)) {
        cout << line << endl;
    }

    cout << "======================================\n";
    in.close();
}