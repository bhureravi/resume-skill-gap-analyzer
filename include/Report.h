#ifndef REPORT_H
#define REPORT_H

#include <string>
#include <vector>
#include "Resume.h"
#include "Role.h"
#include "Company.h"
#include "Analyzer.h"
#include "RecommendationEngine.h"

using namespace std;

class Report {
public:
    void generateConsoleReport(Resume resume, Role role, Company company, Analyzer analyzer, RecommendationEngine recommender);
    void saveReportToFile(string filename, Resume resume, Role role, Company company, Analyzer analyzer, RecommendationEngine recommender);
};

#endif