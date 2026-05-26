#ifndef SKILL_EXTRACTOR_H
#define SKILL_EXTRACTOR_H

#include <string>
#include <vector>
using namespace std;

class SkillExtractor {
public:
    string toLowerCase(string text);
    string removeExtraSymbols(string text);

    vector<string> loadSkillsFromFile(string filename);
    vector<string> extractSkills(string text, vector<string> skillDatabase);
};

#endif