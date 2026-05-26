#ifndef HISTORY_MANAGER_H
#define HISTORY_MANAGER_H

#include <string>
#include "Resume.h"
#include "Role.h"
#include "Company.h"
#include "Analyzer.h"
using namespace std;

class HistoryManager {
public:
    void saveRunToHistory(string filename, Resume resume, Role role, Company company, Analyzer analyzer);
    void showHistory(string filename);
};

#endif