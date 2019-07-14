import pandas as pd 
import matplotlib.pyplot as plt 

class fracfocus_data_search:
    """
    This class generates an object that is used the filter the master
    fracfocus dataframe so it only contains a certain state/state abbreviation,
    county (list), and/or operator
    """

    def __init__(self, state=None, state_abbreviation=None, county_list=None,
                 operator=None):
        #All data in initialize def optional depending on what kind of filtering
        #we want to do
        self.state = state
        self.state_abbreviation = state_abbreviation
        self.county_list=county_list
        self.operator=operator

    def filter_dataframe(self, df, column_state, 
                        column_county, column_operator):
        """
        Filter the data by parameters
        Arguments:
            df: Pandas dataframe that we want to to subset by
            column_state: String. Name of the column for state
            column_county: String. Name of column for county
            column_operator: String. Name of column for operator
        Outputs:
            df_subset: Pandas dataframe. Dataframe after it's been subsetted.
        """
        #Filter by all the parameters and return the subset
        df_subset=df[
                #By state
                (((df[column_state].str.lower())==self.state.lower()) | 
                ((df[column_state].str.lower())==self.state_abbreviation.lower())) &
                #By county
                ((df[column_county].str.lower()).isin(map(str.lower,self.county_list))) &
                #By operator
                ((df[column_operator].str.lower()).str.contains(self.operator.lower()))  
                ]
        return df_subset

def clean_vendor_data(df, column, column_search_string, column_string_rename):
    """
    This function is used to search the vendor data for a specific keyword, and 
    if it's found, change the row value to that specific keyword. Used to clean up the data
    if a vendor is added in multiple different ways.
    Arguments:
        df: Pandas dataframe.
        column: String. Name of the column that we're cleaning up
        column_search_string: String. String that we're looking to match in the column
        column_string_rename: String. What we want to rename the string to if we find 
        any string matches in the column
    Outputs:
        df: Pandas dataframe. Dataframe with returned cleaned up column
    """
    df.loc[df[column].str.contains(column_search_string), column] = column_string_rename
    return df

def generate_scatter_plot(df, x_variable, y_variables, plot_title):
    """
    This function is used to map x- and y-variables against each other
    Arguments:
        df: Pandas dataframe.
        x_variable: String. Name of the column that we want to set as the 
        x-variable in the plot
        y_variables: string (single), or list of strings (multiple). Name(s) 
        of the column(s) that we want to set as the y-variable in the plot
    Outputs:
        Scatter plot in console.
    """
    #Plot results
    df.plot(x=x_variable, y=y_variables, title=plot_title)
    plt.show()

def generate_boxplot(df, x_variable):
    """
    This function generates a basic histogram of a column's data, with
    outliers removed
    Arguments:
        df: Pandas dataframe
        x_variable: String. Name of the column that we want to generate 
        boxplot from
    Outputs:
        Box plot in console.
    """  
    plt.boxplot(list(df[x_variable].dropna()), showfliers=False)
    plt.show()
    
def generate_bar_graph(df, title):
    """
    This function creates a bar graph from pandas dataframe columns.
    Arguments:
        df: Pandas dataframe. Index will be x-axis. Categories and 
        associated amounts are from columns
        title: String. Name of the bar graph
    Outputs:
        Bar graph in console.
    """
    df.plot.bar(rot=0)
    plt.title(title, color='black')
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.show()
    
def main():
    """ 
    Main definition, where we subset the data, analyze it, and generate plots from
    """
    #Pull all of the fracfocus data from a csv
    fracfocus_registry=pd.read_csv('fracfocus_data_example.csv', low_memory=False)
    #Make all of the state column lowercase
    fracfocus_filter=fracfocus_data_search(state='Texas', state_abbreviation='TX',
                          county_list=['Andrews', 'Borden', 'Crane', 'Dawson',
                                       'Ector', 'Eddy', 'Gaines', 'Glasscock'],
                          operator='XTO')
    #Filter dataframe by its parameters
    subsetted_df=fracfocus_filter.filter_dataframe(fracfocus_registry, column_state='StateName', 
                        column_county='CountyName', column_operator='OperatorName')
    #Convert the data column to a pandas datetime
    subsetted_df['JobStartDate']=pd.to_datetime(subsetted_df['JobStartDate'])
    #Now that we have our desired dataframe, it's time to analyze the data
    #Let's calculate the average amount of liquids that the operator pumps in fracs 
    #over time
    basic_frac_characteristics=subsetted_df[['JobStartDate', 'JobEndDate', 'APINumber', 
                                             'TotalBaseNonWaterVolume', 'TVD',
                                             'TotalBaseWaterVolume', 
                                             'Latitude', 'Longitude']].drop_duplicates()
    #Plot the 'TotalBaseWaterVolume' variable over time
    generate_scatter_plot(basic_frac_characteristics, x_variable='JobStartDate', 
              y_variables=['TotalBaseWaterVolume'], 
              plot_title='Total Base Water Volume for Fracs over Time')
    #Plot the 'TotalBaseNonWaterVolume' variable over time
    generate_scatter_plot(basic_frac_characteristics, x_variable='JobStartDate', 
              y_variables=['TotalBaseNonWaterVolume'], 
              plot_title='Total Base Non-Water Volume for Fracs over Time')
    #Plot the distribution of TotalBaseNoneWaterVolume using a box-and-whisker plot, with outliers removed
    generate_boxplot(basic_frac_characteristics, x_variable='TotalBaseNonWaterVolume')
    
    #PERFORM VENDOR ANALYSIS BELOW
    #Subset the data set to get unique rows for vendor data
    vendor_data=subsetted_df[['JobStartDate', 'JobEndDate', 'APINumber', 
                              'Latitude', 'Longitude', 'Supplier', 'TradeName']].drop_duplicates()
    #PERFORM SOME DATA CLEANING ON THE VENDOR DATA
    #Remove NaN supplier values
    vendor_data=vendor_data.dropna(subset=['Supplier'])
    #Make all Supplier data uppercase
    vendor_data['Supplier']=vendor_data['Supplier'].str.upper()
    #Use the clean_vendor_data() function to clean up the vendor categories so they're more standardized
    vendor_lookup_dict={'RISING STAR': 'RISING STAR', 
                             'CHEMPLEX': 'CHEMPLEX',
                             'SAN.*TROL': 'SANDTROL',
                             'MULTI.*CHEM': 'MULTI-CHEM',
                             'XTO': 'OPERATOR',
                             'PFP': 'PFP',
                             'CESI': 'CESI',
                             'NALCO': 'NALCO', 
                             'FRITZ': 'FRITZ INDUSTRIES',
                             'ASK': 'ASK',
                             'ACE': 'ACE',
                             'BRENNTAG': 'BRENNTAG', 
                             'COIL.*CHEM': 'COILCHEM',
                             'COOPER': 'COOPER NATURAL RESOURCES',
                             'ECONOMY': 'ECONOMY POLYMERS',
                             'FINORIC': 'FINORIC',
                             'EES': 'ENVIRONMENTAL ENERGY SERVICE',
                             'PREFERRED': 'PREFERRED SANDS', 
                             'ROCKWATER': 'ROCKWATER',
                             'SNF': 'SNF',
                             'MULTIPLE': 'MULTIPLE SUPPLIERS',
                             'REAGENT': 'REAGENT',
                             'PRO.*FRAC': 'PROFRAC'}
    #Loop through the dictionary and change the name accordingly based on character lookups
    for vendor_lookup, vendor_name in vendor_lookup_dict.items():
        vendor_data=clean_vendor_data(vendor_data, 'Supplier', vendor_lookup, vendor_name)
    #Make a column converting data to monthly (this will be the x-axis for the bar graph)
    vendor_data['JobStartDateQuarter'] = vendor_data['JobStartDate'].dt.to_period('Q')
    #Subset to only include 2018 data
    vendor_data=vendor_data[(vendor_data.JobStartDate>=pd.to_datetime('2018-01-01')) & 
                            (vendor_data.JobStartDate<=pd.to_datetime('2019-01-01'))]
    #Count the number of purchases that the operator makes over time from each vendor
    vendor_data['NumberTimesSupplierUsed']=vendor_data[['JobStartDateQuarter', 'Supplier']].groupby([
            'JobStartDateQuarter', 'Supplier'])['Supplier'].transform('count')
    #Subset the data to only include vendor counts by quarter
    vendor_data_stacked_bar_graph=vendor_data[['Supplier', 'JobStartDateQuarter', 
                                    'NumberTimesSupplierUsed']].drop_duplicates()
    #Pivot the data from long to wide format
    vendor_data_stacked_bar_graph_pivoted=vendor_data_stacked_bar_graph.pivot(
                                                            index='JobStartDateQuarter', 
                                                            columns='Supplier', 
                                                            values='NumberTimesSupplierUsed').fillna(0)
    #Filter to only include suppliers purchased from more than 20 times
    total_col_sums=pd.DataFrame(vendor_data_stacked_bar_graph_pivoted.sum()>=20)
    vendor_data_stacked_bar_graph_pivoted=vendor_data_stacked_bar_graph_pivoted.drop(list(
            total_col_sums[total_col_sums[0]==False].index), axis=1)
    #Plot the vendor data in a bar chart
    generate_bar_graph(vendor_data_stacked_bar_graph_pivoted, 
                       title='Number of Times Vendor Was Purchased From Over Quarter')
    
#Run main
if __name__== "__main__":
    main()
    
    