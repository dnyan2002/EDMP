import pandas as pd

# Test case data
data = [
    ["TC013", "Dashboard", "Display of data according to database", "Open the Dashboard screen", "All data is shown as per database values", ""],
    ["TC013", "Dashboard", "Graphs display as per database", "Check each graph", "Graph data matches the database", ""],
    ["TC013", "Dashboard", "Auto-refresh functionality", "Wait for 1 hour", "Screen refreshes automatically every hour", ""],
    ["TC013", "Dashboard", "Data placeholder when missing", "View dashboard when data is missing", "Shows `?` instead of blank or incorrect value", ""],
    ["TC013", "Dashboard", "Access control", "Try accessing screen without login", "Dashboard is not visible when user is not logged in", ""],
    ["TC013", "Dashboard", "Parameters and units display", "Check each card/graph for units", "Units and parameters display correctly", ""],
    
    ["TC014", "Slurry Section", "Proper alignment of parameters", "Check UI layout", "All parameters are aligned properly", ""],
    ["TC014", "Slurry Section", "Missing data display", "View screen when parameter is not available", "`?` displayed in place of unavailable value", ""],
    ["TC014", "Slurry Section", "Data refresh functionality", "Wait 1 minute", "All values refresh every minute", ""],
    ["TC014", "Slurry Section", "Flow meter status color indication", "Simulate running/stopped flow meter", "Green = Running, Red = Stopped", ""],
    ["TC014", "Slurry Section", "Totalizer calculation", "Monitor parameter increase", "Totalizer updates correctly based on other parameters", ""],

    ["TC015", "Purification Screen", "Alignment of all parameters", "Check UI alignment", "All values aligned correctly", ""],
    ["TC015", "Purification Screen", "Missing data placeholder", "Simulate unavailable data", "`?` is shown in place of missing data", ""],
    ["TC015", "Purification Screen", "Refresh interval", "Wait 1 minute", "Data refreshes every minute", ""],
    ["TC015", "Purification Screen", "Flow meter color status", "Toggle flow meter status", "Green = Running, Red = Stopped", ""],
    ["TC015", "Purification Screen", "Totalizer calculation", "Monitor for increasing values", "Correct and increasing values as per calculation", ""],

    ["TC016", "Reports Screen", "Report generation", "Generate a report", "Reports generate correctly", ""],
    ["TC016", "Reports Screen", "Filter-based report generation", "Apply different filters", "Reports reflect applied filters", ""],
    ["TC016", "Reports Screen", "Report export to Excel/PDF", "Export the report", "Files downloaded with correct format and data", ""],
    ["TC016", "Reports Screen", "Graph display", "Generate graph from report", "Graph data matches report", ""],

    ["TC017", "Users Screen", "User management", "Create, edit, delete users", "Actions completed successfully with appropriate confirmation messages", ""],
    ["TC017", "Users Screen", "Access control", "Try accessing without permission", "Screen not accessible if access not granted", ""],
    ["TC017", "Users Screen", "User list visibility", "View user list", "Complete and accurate list shown", ""],
    ["TC017", "Users Screen", "Success messages", "Edit or delete a user", "Success messages shown correctly", ""],

    ["TC018", "Admin Panel", "Access restricted to Admin role", "Login as normal user and admin", "Only admin can access", ""],
    ["TC018", "Admin Panel", "Admin data access", "Navigate through admin features", "Admin can view necessary model data", ""],
    ["TC018", "Admin Panel", "Admin permissions", "Try editing/deleting data", "Works only if permissions are assigned", ""],

    ["TC019", "Manual Entry Screen", "Manual data entry", "Add values to forms", "Data saved correctly", ""],
    ["TC019", "Manual Entry Screen", "Display of last 5 entries", "Submit several entries, then view screen", "Last 5 entries are visible", ""],

    ["TC020", "Contact", "Contact popup display", "Click on Contact", "Contact details shown in popup", ""],
    ["TC020", "Contact", "Hyperlink functionality", "Click on email and website links", "Links redirect to respective destination", ""],

    ["TC021", "Login Screen", "Login form display", "Go to login screen", "Login form appears correctly", ""],
    ["TC021", "Login Screen", "Post-login redirection", "Login with valid credentials", "Redirects to correct screen", ""],

    ["TC022", "All Screens", "Date and Time display", "View any screen", "Current time and date shown correctly", ""],
    ["TC022", "All Screens", "UI elements - Navigation, Headings, Sidebar", "View UI layout", "All elements are displayed properly and consistently", ""],
    ["TC022", "All Screens", "Logo and title alignment", "Observe header", "Logo and titles are properly aligned", ""]
]

# Create DataFrame and export to Excel
df = pd.DataFrame(data, columns=["Test Case ID", "Screen Name", "Test Item", "Steps to Test", "Expected Result", "Pass/Fail"])
df.to_excel("Test_Cases_Document.xlsx", index=False)
