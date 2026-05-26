#include <iostream>
#include <fstream>
#include "../include/Report.h"
using namespace std;

void Report::generateConsoleReport(Resume resume, Role role, Company company, Analyzer analyzer, RecommendationEngine recommender) {
    cout << "\n=====================================\n";
    cout << " FINAL REPORT\n";
    cout << "=====================================\n";

    cout << "\nSelected Role: " << role.getRoleName() << endl;
    cout << "Selected Company: " << company.getCompanyName() << endl;

    cout << "\nScores:\n";
    cout << "Role Match Score: " << analyzer.getRoleMatchScore() << "%\n";
    cout << "Company Match Score: " << analyzer.getCompanyMatchScore() << "%\n";
    cout << "Overall Score: " << analyzer.getOverallScore() << "%\n";

    cout << "\nMissing Role Skills:\n";
    vector<string> missingRole = analyzer.getMissingRoleSkills();
    if (missingRole.empty()) {
        cout << "None\n";
    } else {
        for (string skill : missingRole) {
            cout << "- " << skill << endl;
        }
    }

    cout << "\nMissing Company Skills:\n";
    vector<string> missingCompany = analyzer.getMissingCompanySkills();
    if (missingCompany.empty()) {
        cout << "None\n";
    } else {
        for (string skill : missingCompany) {
            cout << "- " << skill << endl;
        }
    }

    cout << "\nRecommendations:\n";
    vector<string> recs = recommender.generateRecommendations(resume, role, company, analyzer);
    if (recs.empty()) {
        cout << "No recommendations available.\n";
    } else {
        for (string rec : recs) {
            cout << "- " << rec << endl;
        }
    }

    cout << "=====================================\n";
}

void Report::saveReportToFile(string filename, Resume resume, Role role, Company company, Analyzer analyzer, RecommendationEngine recommender) {
    ofstream out(filename);

    if (!out.is_open()) {
        cout << "Could not open file for writing.\n";
        return;
    }

    out << "=====================================\n";
    out << "FINAL REPORT\n";
    out << "=====================================\n";

    out << "\nSelected Role: " << role.getRoleName() << "\n";
    out << "Selected Company: " << company.getCompanyName() << "\n";

    out << "\nScores:\n";
    out << "Role Match Score: " << analyzer.getRoleMatchScore() << "%\n";
    out << "Company Match Score: " << analyzer.getCompanyMatchScore() << "%\n";
    out << "Overall Score: " << analyzer.getOverallScore() << "%\n";

    out << "\nMissing Role Skills:\n";
    vector<string> missingRole = analyzer.getMissingRoleSkills();
    if (missingRole.empty()) {
        out << "None\n";
    } else {
        for (string skill : missingRole) {
            out << "- " << skill << "\n";
        }
    }

    out << "\nMissing Company Skills:\n";
    vector<string> missingCompany = analyzer.getMissingCompanySkills();
    if (missingCompany.empty()) {
        out << "None\n";
    } else {
        for (string skill : missingCompany) {
            out << "- " << skill << "\n";
        }
    }

    out << "\nRecommendations:\n";
    vector<string> recs = recommender.generateRecommendations(resume, role, company, analyzer);
    if (recs.empty()) {
        out << "No recommendations available.\n";
    } else {
        for (string rec : recs) {
            out << "- " << rec << "\n";
        }
    }

    out << "=====================================\n";
    out.close();

    cout << "Report saved successfully to " << filename << endl;
}