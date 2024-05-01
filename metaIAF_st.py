import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import NormalDist

#add title to app
st.subheader("Compute random-effects meta-analysis given _n_ and _r_")
st.markdown("Autopopulated with data from Samaha & Romei (2024) _Journal of Cognitive Neuroscience_, who performed a meta-analysis of studies correlating individual alpha frequency with temporal properties of perception.")
st.markdown("Plots and statistics will update after any change to the table. To delete a row, click the gray square to the left of the row and press delete on your keyboard. To add data, click on the empty gray cell at the bottom of the table. Refresh the page to repopulate the original data. Copy/paste supported.")

#establish columns
col1, col2 = st.columns([0.6, 0.4])

#populate original database from Samaha & Romei (2023) JoCN
df = pd.DataFrame(
    [
       
       {"Study name": "Sokoliuk & VanRullen (2013)",  "n": 10, "r": 0.81},
       {"Study name": "Minami & Amano (2017)",        "n": 12, "r": 0.84},
       {"Study name": "Gotz et al. (2013)",           "n": 23, "r": 0.60},
       {"Study name": "May et al. (2015)",            "n": 28, "r": 0.44},
       {"Study name": "Baumgarten et al. (2018)",     "n": 43, "r": 0.41},
       {"Study name": "Shen et al. (2019)",           "n": 17, "r": 0.72},
       {"Study name": "Zhang et al. (2019)",          "n": 18, "r": 0.55},
       {"Study name": "Ro (2019)",                    "n": 9,  "r": 0.58},
       {"Study name": "Gulbinaite et al. (2017)",     "n": 30, "r": 0.43},
       {"Study name": "Samaha & Postle (2015)",       "n": 20, "r": 0.56},
       {"Study name": "Gray & Emmanouil (2019)",      "n": 32, "r": 0.24},
       {"Study name": "Drewes et al. (2022)",         "n": 16, "r": 0.43},
       {"Study name": "Deodato & Melcher (2023)",     "n": 28, "r": 0.47},
       {"Study name": "Buergers & Noppeney (2022)",   "n": 20, "r": 0.12},
       {"Study name": "Cecere et al. (2015) exp. 1",  "n": 22, "r": 0.70},
       {"Study name": "Cecere et al. (2015) exp. 2",  "n": 12, "r": 0.71},
       {"Study name": "Venskus & Hughes (2021)",      "n": 38, "r": 0.32},
       {"Study name": "Cooke et al. (2019)",          "n": 51, "r": 0.52},
       {"Study name": "Keil & Senkowski (2017)",      "n": 26, "r": 0.53},
       {"Study name": "Noguchi (2022)",               "n": 29, "r": 0.20},
       {"Study name": "Kristofferson (1967a)",        "n": 8,  "r": 0.64},
       {"Study name": "Kristofferson (1967b)",        "n": 13, "r": 0.74},
       {"Study name": "Bastiaansen et al. (2020)",    "n": 22, "r": 0.44},
       {"Study name": "Grabot et al. (2017)",         "n": 10, "r": 0.09},
       {"Study name": "London et al. (2022)",         "n": 40, "r": 0.24},
       {"Study name": "Ronconi et al. (2023) exp. 1", "n": 17, "r": 0.85},
       {"Study name": "Ronconi et al. (2023) exp. 2", "n": 17, "r": 0.35},
       
   ]
)

config = {'Study name' : st.column_config.Column(help="Shorthand name for the study (just for display - not required)"),
          'r' : st.column_config.NumberColumn(min_value=-1, max_value=1, help="Correlation _r_-value (typically Pearson's _r_)"),
          'n' : st.column_config.NumberColumn(min_value=2, help="Sample size of the study")}
with col1:
    edited_df = st.data_editor(df, column_config = config, num_rows="dynamic", use_container_width=1, height=500)
    st.caption('Scroll table for more data')


#compute meta-analytic stats
#er = pd.to_numeric(edited_df.r, errors='coerce').dropna()
#en = pd.to_numeric(edited_df.n, errors='coerce').dropna()
 
er = np.array(edited_df.r,dtype=float)
en = np.array(edited_df.n,dtype=float)
ind2keep = (~np.isnan(er)) & (~np.isnan(en))
er = er[ind2keep]
en = en[ind2keep]


meta_r = sum(er*en)/sum(en)
SDr = np.sqrt((sum(en*((er-meta_r)**2))) / sum(en))
SEr = SDr/np.sqrt(np.size(er))
Z = meta_r/SEr
p = (1-NormalDist().cdf(abs(Z)))*2


# plotting
#setup columns for table (left) and figures (right)
fcol1, fcol2= st.columns(2)

fig, ax = plt.subplots()
ax.set_title('Distribution of r-values from table')
ax.set_xlabel('Correlation')
ax.set_ylabel('Count')
ax.set_xlim(-1, 1)
ax.grid('true')
ax.set_axisbelow('True')
ax.set_xticks(np.linspace(-1, 1, 9))
ax.hist(edited_df.r,np.linspace(-1,1,27), color='purple')

#st.pyplot(fig)

#bootstrap analysis
nent = len(er)
meta_r_boot=[]
nboot = 10000


for x in range(nboot):
    
    bind=np.random.choice(nent,nent)
    bsampr = er[bind]
    bsampn = en[bind]

    bmeta = round(sum(bsampr*bsampn)/sum(bsampn),3)

    meta_r_boot.append(bmeta)


fig2, ax = plt.subplots()
ax.set_title('Bootstrap distribution of population correlation')
ax.set_xlabel('Population correlation')
ax.set_ylabel('Count (out of 10000)')
ax.set_xlim(-1, 1)
ax.grid('true')
ax.set_axisbelow('True')
ax.set_xticks(np.linspace(-1, 1, 9))
ax.hist(meta_r_boot,np.linspace(-1,1,100), color='blue')

lowerCI = round(np.percentile(meta_r_boot, 2.5),3)
upperCI = round(np.percentile(meta_r_boot, 97.5),3)

#col1, col2, col3, col4, col5 = st.columns(5)
col2.metric("Population correlation estimate", value = round(meta_r,3), help = "Eq. 11 from Field (2011) _Psychological Methods_. Our current best guess at the true correlation strength")
col2.metric("Bootstrap 95% CI", value = str([lowerCI, upperCI]), help = "Range of plausible values of the population correlation")
col2.metric("Standard error", value=round(SEr,3), help = "Eq. 12 and 13 from Field (2011) _Psychological Methods_. A parametric estimate of the standard error of the mean population correlation")
col2.metric("Z-statistic", value=round(Z,3), help = "Eq. 14 from Field (2011) _Psychological Methods_. An estimate of the number of standard deviations away from zero the population correlation is")
col2.metric("p-value", value=round(p,5), help = "Probability of observing a population effect this size if the null hypothesis is actually true" )

fcol1.pyplot(fig)
fcol2.pyplot(fig2)

st.markdown("Contact Jason Samaha (jsamaha@ucsc.edu) to report bugs or suggest additions to the default table. See https://github.com/samahaha/randFX_meta_app for source code.")
