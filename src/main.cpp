#include <iostream>
using namespace std;

int main() {
    cout << "=====================================\n";
    cout << " Resume Skill Gap Analyzer\n";
    cout << "=====================================\n";

    cout << "\n1. Load Resume\n";
    cout << "2. Choose Role\n";
    cout << "3. Choose Company\n";
    cout << "4. Analyze\n";
    cout << "5. Save Report\n";
    cout << "6. Exit\n";

    cout << "\nEnter your choice: ";

    int choice;
    cin >> choice;

    cout << "You selected option: " << choice << endl;

    return 0;
}