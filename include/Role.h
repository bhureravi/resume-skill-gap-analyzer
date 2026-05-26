#ifndef ROLE_H
#define ROLE_H

#include <string>
#include <vector>
using namespace std;

class Role {
private:
    string roleName;
    vector<string> requiredSkills;
    vector<string> preferredSkills;

public:
    Role();
    Role(string name);

    void setRoleName(string name);
    string getRoleName();

    void setRequiredSkills(vector<string> skills);
    vector<string> getRequiredSkills();

    void setPreferredSkills(vector<string> skills);
    vector<string> getPreferredSkills();

    bool loadFromFile(string filename);
    void displayRole();
};

#endif