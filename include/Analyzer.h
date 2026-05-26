#ifndef ANALYZER_H
#define ANALYZER_H

#include <string>
#include <vector>
#include "Resume.h"
#include "Role.h"
#include "Company.h"
using namespace std;

class Analyzer {
private:
    vector<string> missingRoleSkills;
    vector<string> missingCompanySkills;
    int roleMatchScore;
    int companyMatchScore;
    int overallScore;

public:
    Analyzer();

    void analyze(Resume resume, Role role, Company company);

    int getRoleMatchScore();
    int getCompanyMatchScore();
    int getOverallScore();

    vector<string> getMissingRoleSkills();
    vector<string> getMissingCompanySkills();

    void displayAnalysis();
};

#endif