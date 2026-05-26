#ifndef INSIGHT_ENGINE_H
#define INSIGHT_ENGINE_H

#include <string>
#include <vector>
#include "Resume.h"
#include "Role.h"
#include "Company.h"
#include "Analyzer.h"
using namespace std;

class InsightEngine {
private:
    string readinessLevel;
    vector<string> topPriorities;

    bool alreadyAdded(string item, vector<string> items);
    string toLowerCase(string text);

public:
    InsightEngine();

    void buildInsights(Resume resume, Role role, Company company, Analyzer analyzer);

    string getReadinessLevel();
    vector<string> getTopPriorities();

    void displayInsights();
};

#endif