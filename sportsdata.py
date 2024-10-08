# import required packages
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# import cycling data
cycling_stats = pd.read_csv('/Users/victordecolvenaer/Documents/python_scripts/personal_sport_data/Activities cycling.csv')

#Create PDF file with output plots
pdf_filename = 'output_plots.pdf'

#remove columns from dataframe
cycling_stats = cycling_stats.drop(columns= ['Activiteittype','Favoriet','Titel','Gem. staplengte','Gemiddelde verticale ratio','Gem. verticale oscillatie','Gem. grondcontacttijd','Training Stress Score®','Grit','Flow','Gemiddelde Swolf', 'Gem. slagsnelheid', 'Totaal herhalingen', 'Decompressie', 'Minimum hoogte', 'Maximum hoogte'])

# group, sum average afstand by year
cycling_stats['Jaar'] = pd.to_datetime(cycling_stats['Datum']).dt.year
cycling_stats_grouped = cycling_stats.groupby('Jaar',as_index=False)['Afstand'].sum()
cycling_stats_grouped['Gemiddelde afstand'] = cycling_stats.groupby('Jaar',as_index=False)['Afstand'].mean()['Afstand']

# group, sum, average by month & year
cycling_stats['Datum'] = pd.to_datetime(cycling_stats['Datum']).dt.to_period('M').astype(str)
cycling_stats_grouped_month = cycling_stats.groupby(['Datum'],as_index=False)['Afstand'].sum()
cycling_stats_grouped_month['Gemiddelde afstand'] = cycling_stats.groupby(['Datum'],as_index=False)['Afstand'].mean()['Afstand']

# create a continuous range with dates to use for x axis
full_date_range = pd.date_range(
    start=cycling_stats_grouped_month['Datum'].min(), 
    end=cycling_stats_grouped_month['Datum'].max(), 
    freq='ME'
)
full_date_range = full_date_range.strftime('%Y-%m')

# create merged DF
full_dates_df = pd.DataFrame(full_date_range, columns=['Datum'])
cycling_stats_grouped_month = pd.merge(full_dates_df, cycling_stats_grouped_month, on='Datum', how='left')
cycling_stats_grouped_month = cycling_stats_grouped_month.fillna(0)

# clean data frame and convert dtypes to float
cycling_stats = cycling_stats.replace('--',pd.NA)
cycling_stats = cycling_stats.dropna(how= 'any')
cycling_stats['Calorieën'] = cycling_stats['Calorieën'].str.replace(',','')

columns = cycling_stats.columns
for col in columns:
    try:
        cycling_stats[col] = cycling_stats[col].astype(float)
    except ValueError:
        cycling_stats[col] = cycling_stats[col]

"""Visualize data"""
# create lists of columns to analyse
grouped_columns = ['Afstand', 'Gemiddelde afstand']

# exploratory visualisation: histogram to have insight in data distribution
with PdfPages(pdf_filename) as pdf_pages:
    plt.figure()
    #ax = fig.gca()
    cycling_stats.hist()
    pdf_pages.savefig()
    plt.close()

    for column in grouped_columns:
        # initiate figure and plot barchart
        plt.figure()
        plt.bar(cycling_stats_grouped['Jaar'], cycling_stats_grouped[column])

        # configure x axis values to be discrete years
        plt.xticks(cycling_stats_grouped['Jaar'].astype(int))

        # add labels and title
        plt.xlabel ('Jaar')
        plt.ylabel('Aantal KMs')
        plt.title('aantal KM gereden per jaar')
        pdf_pages.savefig()
        plt.close()

    for column in grouped_columns:
        # initiate figure and plot barchart
        plt.figure()
        plt.bar(cycling_stats_grouped_month['Datum'], cycling_stats_grouped_month[column])
    
        # configure x axis values to be discrete years
        plt.xticks(rotation = 90, ha = 'right', fontsize = '5')

        # add labels and title
        plt.xlabel ('Jaar & maand')
        plt.ylabel('Aantal KMs')
        plt.title('aantal KM gereden per maand')
        pdf_pages.savefig()
        plt.close()
    
    plt.figure()
    sns.pairplot(cycling_stats)
    pdf_pages.savefig()
    plt.close()

    #experimenting with sklearn    

    # Select relevant features
    features = ['Afstand', 'Gemiddelde snelheid', 'Max. snelheid', 'Calorieën', 'Gem. HS', 'Gemiddelde fietscadans']

    # Standardize the features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(cycling_stats[features])

    # Determine optimal number of clusters using the Elbow Method
    sse = []
    for k in range(1, 10):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(scaled_features)
        sse.append(kmeans.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, 10), sse, marker='o')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Sum of Squared Distances')
    plt.title('Elbow Method for Optimal k')
    pdf_pages.savefig()
    plt.close()

    # Apply KMeans with chosen number of clusters
    kmeans = KMeans(n_clusters=3, random_state=42)  # Adjust clusters based on the elbow plot
    clusters = kmeans.fit_predict(scaled_features)

    # Add cluster assignments to the original DataFrame
    cycling_stats['Cluster'] = clusters

    #visualize clusters
    sns.pairplot(cycling_stats, vars=features, hue='Cluster', palette='Set1', diag_kind='kde', plot_kws={'alpha': 0.6, 's': 50, 'edgecolor': 'k'})
    plt.suptitle('Scatter Plot Matrix of Features by Cluster', y=1.02)
    pdf_pages.savefig()
    plt.close()

#visualize boxplots of clusters
    for feature in features:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Cluster', y=feature, data=cycling_stats, palette='Set1')
        plt.title(f'Box Plot of {feature} by Cluster')
        pdf_pages.savefig()
        plt.close()