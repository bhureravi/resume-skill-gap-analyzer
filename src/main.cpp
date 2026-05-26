#include <iostream>
#include <limits>
#include "../include/Resume.h"
#include "../include/SkillExtractor.h"
#include "../include/Role.h"
#include "../include/Company.h"
#include "../include/Analyzer.h"
#include "../include/RecommendationEngine.h"
#include "../include/Report.h"
#include "../include/HistoryManager.h"
#include "../include/InsightEngine.h"
#include "../include/ConfigManager.h"

using namespace std;

void printHeader() {
    cout << "\n=====================================\n";
    cout << "   Resume Skill Gap Analyzer\n";
    cout << "=====================================\n";
}

void printStatus(Resume &resume, Role &role, Company &company, bool skillsExtracted, bool analyzed) {
    cout << "\nCurrent Status:\n";
    cout << "Resume: " << (resume.getRawText().empty() ? "Not loaded" : "Loaded") << endl;
    cout << "Role: " << (role.getRoleName().empty() ? "Not selected" : "Selected") << endl;
    cout << "Company: " << (company.getCompanyName().empty() ? "Not selected" : "Selected") << endl;
    cout << "Skills Extracted: " << (skillsExtracted ? "Yes" : "No") << endl;
    cout << "Analysis Done: " << (analyzed ? "Yes" : "No") << endl;
}

void runDemoMode(
    Resume &resume,
    SkillExtractor &extractor,
    Role &role,
    Company &company,
    Analyzer &analyzer,
    RecommendationEngine &recommender,
    Report &report,
    bool &skillsExtracted,
    bool &analyzed,
    ConfigManager &config
) {
    cout << "\nRunning demo mode...\n";

    string resumeFile = config.getValue("resume");
    string roleFile = config.getValue("role");
    string companyFile = config.getValue("company");
    string skillsFile = config.getValue("skills");

    if (resumeFile == "" || roleFile == "" || companyFile == "" || skillsFile == "") {
        cout << "Config file is missing one or more required paths.\n";
        return;
    }

    if (!resume.loadFromFile(resumeFile)) {
        cout << "Demo resume could not be loaded.\n";
        return;
    }

    if (!role.loadFromFile(roleFile)) {
        cout << "Demo role could not be loaded.\n";
        return;
    }

    if (!company.loadFromFile(companyFile)) {
        cout << "Demo company could not be loaded.\n";
        return;
    }

    vector<string> skillDatabase = extractor.loadSkillsFromFile(skillsFile);
    if (skillDatabase.empty()) {
        cout << "Skill database not found.\n";
        return;
    }

    vector<string> foundSkills = extractor.extractSkills(resume.getRawText(), skillDatabase);
    resume.setExtractedSkills(foundSkills);
    skillsExtracted = true;

    analyzer.analyze(resume, role, company);
    analyzed = true;

    recommender.generateRecommendations(resume, role, company, analyzer);

    cout << "\nDemo mode completed successfully.\n";
    report.generateConsoleReport(resume, role, company, analyzer, recommender);
}

int main() {
    int choice = 0;

    Resume resume;
    SkillExtractor extractor;
    Role role;
    Company company;
    Analyzer analyzer;
    RecommendationEngine recommender;
    Report report;
    HistoryManager history;
    InsightEngine insight;
    ConfigManager config;

    bool skillsExtracted = false;
    bool analyzed = false;

    if (!config.loadConfig("data/config.txt")) {
        cout << "Warning: config file could not be loaded.\n";
        cout << "Manual input will still work.\n";
    }

    do {
        printHeader();
        printStatus(resume, role, company, skillsExtracted, analyzed);

        cout << "\nMenu:\n";
        cout << "1. Load Resume\n";
        cout << "2. Select Role\n";
        cout << "3. Select Company\n";
        cout << "4. Extract Skills\n";
        cout << "5. View Role\n";
        cout << "6. View Company\n";
        cout << "7. Analyze\n";
        cout << "8. View Recommendations\n";
        cout << "9. View Full Report\n";
        cout << "10. Save Report\n";
        cout << "11. View History\n";
        cout << "12. Save Current Run to History\n";
        cout << "13. Demo Mode\n";
        cout << "14. View Insights\n";
        cout << "15. View Config\n";
        cout << "16. Exit\n";
        cout << "Enter choice: ";

        if (!(cin >> choice)) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "Please enter a valid number.\n";
            continue;
        }

        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        switch (choice) {
            case 1: {
                string filename;
                cout << "Enter resume file path (press Enter to use default): ";
                getline(cin, filename);

                if (filename == "") {
                    filename = config.getValue("resume");
                }

                if (resume.loadFromFile(filename)) {
                    skillsExtracted = false;
                    analyzed = false;
                    cout << "Resume is now stored in memory.\n";
                }
                break;
            }

            case 2: {
                string roleFile;
                cout << "Enter role file path (press Enter to use default): ";
                getline(cin, roleFile);

                if (roleFile == "") {
                    roleFile = config.getValue("role");
                }

                if (role.loadFromFile(roleFile)) {
                    analyzed = false;
                    cout << "Role is now selected.\n";
                }
                break;
            }

            case 3: {
                string companyFile;
                cout << "Enter company file path (press Enter to use default): ";
                getline(cin, companyFile);

                if (companyFile == "") {
                    companyFile = config.getValue("company");
                }

                if (company.loadFromFile(companyFile)) {
                    analyzed = false;
                    cout << "Company is now selected.\n";
                }
                break;
            }

            case 4: {
                if (resume.getRawText().empty()) {
                    cout << "Please load a resume first.\n";
                    break;
                }

                string skillsFile = config.getValue("skills");
                if (skillsFile == "") {
                    skillsFile = "data/skills.txt";
                }

                vector<string> skillDatabase = extractor.loadSkillsFromFile(skillsFile);

                if (skillDatabase.empty()) {
                    cout << "No skills found in skills database.\n";
                    break;
                }

                vector<string> foundSkills = extractor.extractSkills(resume.getRawText(), skillDatabase);
                resume.setExtractedSkills(foundSkills);
                skillsExtracted = true;
                analyzed = false;

                cout << "\nSkills found in resume:\n";
                if (foundSkills.empty()) {
                    cout << "No skills matched.\n";
                } else {
                    for (string skill : foundSkills) {
                        cout << "- " << skill << endl;
                    }
                }
                break;
            }

            case 5:
                role.displayRole();
                break;

            case 6:
                company.displayCompany();
                break;

            case 7: {
                if (resume.getRawText().empty()) {
                    cout << "Please load a resume first.\n";
                    break;
                }
                if (role.getRoleName().empty()) {
                    cout << "Please select a role first.\n";
                    break;
                }
                if (company.getCompanyName().empty()) {
                    cout << "Please select a company first.\n";
                    break;
                }
                if (!skillsExtracted) {
                    cout << "Please extract skills first.\n";
                    break;
                }

                analyzer.analyze(resume, role, company);
                analyzer.displayAnalysis();
                analyzed = true;
                break;
            }

            case 8: {
                if (!analyzed) {
                    cout << "Please run analysis first.\n";
                    break;
                }

                recommender.generateRecommendations(resume, role, company, analyzer);
                recommender.displayRecommendations();
                break;
            }

            case 9: {
                if (!analyzed) {
                    cout << "Please run analysis first.\n";
                    break;
                }

                report.generateConsoleReport(resume, role, company, analyzer, recommender);
                break;
            }

            case 10: {
                if (!analyzed) {
                    cout << "Please run analysis first.\n";
                    break;
                }

                string filename;
                cout << "Enter output report file path (press Enter to use default): ";
                getline(cin, filename);

                if (filename == "") {
                    filename = config.getValue("report");
                }

                report.saveReportToFile(filename, resume, role, company, analyzer, recommender);
                break;
            }

            case 11:
                history.showHistory(config.getValue("history") == "" ? "output/history.txt" : config.getValue("history"));
                break;

            case 12:
                if (!analyzed) {
                    cout << "Please run analysis first.\n";
                    break;
                }

                history.saveRunToHistory(config.getValue("history") == "" ? "output/history.txt" : config.getValue("history"), resume, role, company, analyzer);
                cout << "Current run saved to history.\n";
                break;

            case 13:
                runDemoMode(resume, extractor, role, company, analyzer, recommender, report, skillsExtracted, analyzed, config);
                break;

            case 14:
                if (!analyzed) {
                    cout << "Please run analysis first.\n";
                    break;
                }

                insight.buildInsights(resume, role, company, analyzer);
                insight.displayInsights();
                break;

            case 15:
                config.displayConfig();
                break;

            case 16:
                cout << "Exiting...\n";
                break;

            default:
                cout << "Invalid choice.\n";
        }

    } while (choice != 16);

    return 0;
}