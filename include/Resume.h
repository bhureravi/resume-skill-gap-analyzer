#ifndef RESUME_H
#define RESUME_H

#include <string>
#include <vector>
using namespace std;

class Resume {
private:
    string rawText;
    vector<string> extractedSkills;

public:
    Resume();

    void setRawText(string text);
    string getRawText();

    void setExtractedSkills(vector<string> skills);
    vector<string> getExtractedSkills();

    bool loadFromFile(string filename);
    void displayResume();
};

#endif