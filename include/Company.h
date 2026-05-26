#ifndef COMPANY_H
#define COMPANY_H

#include <string>
#include <vector>
using namespace std;

class Company {
private:
    string companyName;
    vector<string> expectedSkills;
    vector<string> focusAreas;
    vector<string> prepTips;

public:
    Company();
    Company(string name);

    void setCompanyName(string name);
    string getCompanyName();

    void setExpectedSkills(vector<string> skills);
    vector<string> getExpectedSkills();

    void setFocusAreas(vector<string> areas);
    vector<string> getFocusAreas();

    void setPrepTips(vector<string> tips);
    vector<string> getPrepTips();

    bool loadFromFile(string filename);
    void displayCompany();
};

#endif