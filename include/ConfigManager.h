#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <string>
#include <unordered_map>
using namespace std;

class ConfigManager {
private:
    unordered_map<string, string> configData;

public:
    bool loadConfig(string filename);

    string getValue(string key);
    void displayConfig();
};

#endif