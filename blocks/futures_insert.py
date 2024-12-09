import pandas as pd

# Function to read the 'ScripName' column from an .xls file and save processed data to a new Excel file
def read_and_save_scripname_column(file_path, output_file_path):
    try:
        # Read the file using pandas
        data = pd.read_excel(file_path, engine='xlrd')
        
        # Select the 'ScripName' column
        if 'ScripName' in data.columns:
            scrip_name_data = data['ScripName']
            processed_data = []
            
            # Process the data by replacing "26-Dec-2024" with an empty string
            for value in scrip_name_data:
                v = value.replace("26-Dec-2024", "") if isinstance(value, str) else value
                processed_data.append(v)
            
            # Save the processed data to a new DataFrame
            processed_df = pd.DataFrame({'Processed_ScripName': processed_data})
            
            # Save the DataFrame to an Excel file
            processed_df.to_excel(output_file_path, index=False)
            print(f"Processed data saved to {output_file_path}")
        else:
            print("The column 'ScripName' does not exist in the file.")
    except FileNotFoundError:
        print("The file was not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

# File paths
xls_file_path = "/home/akil/Desktop/Upwork/Trading system - Hari/moderntrade/blocks/data/Futures.xls"
output_file_path = "/home/akil/Desktop/Upwork/Trading system - Hari/moderntrade/blocks/data/Processed_Futures.xlsx"

# Call the function to read and save the data
read_and_save_scripname_column(xls_file_path, output_file_path)

