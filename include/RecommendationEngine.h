#ifndef RECOMMENDATION_ENGINE_H
#define RECOMMENDATION_ENGINE_H

#include <string>
#include <vector>
#include "Resume.h"
#include "Role.h"
#include "Company.h"
#include "Analyzer.h"
using namespace std;

class RecommendationEngine {
private:
    vector<string> recommendations;

    string toLowerCase(string text);
    bool isHighPrioritySkill(string skill);
    bool alreadyAdded(string item, vector<string> items);

public:
    RecommendationEngine();

    vector<string> generateRecommendations(Resume resume, Role role, Company company, Analyzer analyzer);
    void displayRecommendations();
};

#endif