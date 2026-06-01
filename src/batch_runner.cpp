#include <iostream>
#include <vector>
#include <string>
#include "../include/Resume.h"
#include "../include/SkillExtractor.h"
#include "../include/Role.h"
#include "../include/Company.h"
#include "../include/Analyzer.h"
#include "../include/RecommendationEngine.h"
#include "../include/InsightEngine.h"

using namespace std;

string joinVector(const vector<string>& items, const string& delimiter) {
    string result;
    for (size_t i = 0; i < items.size(); i++) {
        if (i > 0) {
            result += delimiter;
        }
        result += items[i];
    }
    return result;
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        cerr << "Usage: backend_cli <resume_file> <role_file> <company_file> <skills_file>\n";
        return 1;
    }

    string resumeFile = argv[1];
    string roleFile = argv[2];
    string companyFile = argv[3];
    string skillsFile = argv[4];

    Resume resume;
    SkillExtractor extractor;
    Role role;
    Company company;
    Analyzer analyzer;
    RecommendationEngine recommender;
    InsightEngine insight;

    if (!resume.loadFromFile(resumeFile)) {
        cerr << "ERROR: Could not load resume file.\n";
        return 2;
    }

    if (!role.loadFromFile(roleFile)) {
        cerr << "ERROR: Could not load role file.\n";
        return 3;
    }

    if (!company.loadFromFile(companyFile)) {
        cerr << "ERROR: Could not load company file.\n";
        return 4;
    }

    vector<string> skillDatabase = extractor.loadSkillsFromFile(skillsFile);
    if (skillDatabase.empty()) {
        cerr << "ERROR: Skills database is empty.\n";
        return 5;
    }

    vector<string> foundSkills = extractor.extractSkills(resume.getRawText(), skillDatabase);
    resume.setExtractedSkills(foundSkills);

    analyzer.analyze(resume, role, company);
    recommender.generateRecommendations(resume, role, company, analyzer);
    insight.buildInsights(resume, role, company, analyzer);

    vector<string> recommendations = recommender.generateRecommendations(resume, role, company, analyzer);

    cout << "===RESULT_START===\n";
    cout << "ROLE=" << role.getRoleName() << "\n";
    cout << "COMPANY=" << company.getCompanyName() << "\n";
    cout << "ROLE_SCORE=" << analyzer.getRoleMatchScore() << "\n";
    cout << "COMPANY_SCORE=" << analyzer.getCompanyMatchScore() << "\n";
    cout << "OVERALL_SCORE=" << analyzer.getOverallScore() << "\n";
    cout << "READINESS=" << insight.getReadinessLevel() << "\n";
    cout << "EXTRACTED_SKILLS=" << joinVector(foundSkills, ", ") << "\n";
    cout << "MISSING_ROLE=" << joinVector(analyzer.getMissingRoleSkills(), ", ") << "\n";
    cout << "MISSING_COMPANY=" << joinVector(analyzer.getMissingCompanySkills(), ", ") << "\n";
    cout << "RECOMMENDATIONS=" << joinVector(recommendations, " || ") << "\n";
    cout << "===RESULT_END===\n";

    return 0;
}