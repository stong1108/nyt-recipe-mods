import streamlit as st
from streamlit_card import card

import re
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
client = OpenAI(api_key = os.environ.get('OPENAI_API_KEY'))

## recipe functions
pattern = r'^https://cooking\.nytimes\.com/recipes/\d+[-\w]*'

prompt = """Provided below is a list of the most helpful comments on a recipe
for {}. Summarize the top 5 recipe modifications in a bulleted list.
Only output the bulleted list and nothing else.

Most helpful comments:
{}
"""

def get_completion(prompt, model='gpt-3.5-turbo'):
    messages = [{"role": "system", "content": "You are a cooking enthusiast."},{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

def soup_from_url(recipe_url):
    try:
        r = requests.get(recipe_url)
    except Exception as e:
        raise ValueError(e)

    if r.status_code != 200:
        raise ValueError(f'Bad status code: {r.status_code}')
    
    soup = BeautifulSoup(r.content, features='lxml')
    return soup

def extract_soup_content(soup):
    # get recipe name
    recipe_name = soup.find('h1', {'class': 'pantry--title-display'}).text

    # get img
    img_result = soup.find('img', attrs={'fetchpriority': 'high'})
    if img_result is not None:
        img_url = img_result['src']
    else:
        img_url = None

    # get helpful comments
    section = soup.find('section', {'role': 'tabpanel', 'aria-labelledby': 'helpful'})
    most_helpful_comments = [child.p.text for child in section.children]

    return recipe_name, img_url, most_helpful_comments

def recipe_suggestions(recipe_name, most_helpful_comments, prompt=prompt):
    n_comments = len(most_helpful_comments)
    if n_comments < 5:
        raise ValueError('Not enough helpful comments posted (at least 5 required)')

    concat_most_helpful_comments = '\n'.join(most_helpful_comments)

    suggestions = get_completion(prompt.format(recipe_name, concat_most_helpful_comments))
    return suggestions

# Streamlit App
st.set_page_config(layout='wide')

st.title('NYT Cooking Helper')
if "df" not in st.session_state:
    st.session_state.df = pd.read_csv('nyt_recipes.tsv', sep='\t')


tab1, tab2 = st.tabs(["Generate for new recipe", "Browse existing results"])
with tab2:
    for _, row in st.session_state.df.iterrows():
        res = card(
            title=row['recipe_name'],
            text=row['suggestions'].replace(' - ', '\n- '),
            image=row['img_url'],
            url=row['url'],
            styles={
                "div": {
                    "padding": "0px",
                },
                "card": {
                    "width": "85%",
                    "height": "300px",
                    "margin-top": "0px",
                },
                'title': {
                    'font-family': "Georgia Pro Light, Georgia, serif;",
                    'font-weight': '100'
                },
                "filter": {
                    "background-color": "rgba(0, 0, 0, .45)"
                }
            }
        )

with tab1:
    st.subheader('Directions')
    directions = [
        '1. Go to https://cooking.nytimes.com/',
        '2. Find a recipe with too many "Most Helpful" notes to read through',
        '3. Enter the recipe URL below and wait for generated summary'
    ]
    st.write('\n'.join(directions))

    st.text_input("NYT Recipe URL", "https://cooking.nytimes.com/recipes/1025042-microwave-salmon", key="recipe_url")

    col1, col2, col3 = st.columns([0.2, 0.4, 0.4])

    col1.image('Swedish-chef-2820682089.jpeg')



    # for each recipe url, need to store title, img url, & openai response

    if st.session_state.recipe_url != '':
        pattern = r'^https://cooking\.nytimes\.com/recipes/\d+[-\w]*'
        match_obj = re.match(pattern, st.session_state.recipe_url, re.IGNORECASE)
        if not match_obj:
            st.write(f'{st.session_state.recipe_url} does not appear to be a URL for a NYT Cooking recipe.')

        else:
            # first check if recipe has already been run
            df_matches = st.session_state.df[st.session_state.df['url'] == st.session_state.recipe_url]
            if len(df_matches) != 0:
                result = df_matches.iloc[0]
                recipe_name = result['recipe_name']
                img_url = result['img_url']
                suggestions = result['suggestions']
                most_helpful_comments = None

            else: 
                try:
                    soup = soup_from_url(st.session_state.recipe_url)
                    recipe_name, img_url, most_helpful_comments = extract_soup_content(soup)

                except ValueError as e:
                    st.write(f'Unable to continue due to error- {e}')

            with col2:
                res = card(
                    title=recipe_name,
                    text='',
                    image=img_url,
                    url=st.session_state.recipe_url,
                    styles={
                        "div": {
                            "padding": "0px",
                        },
                        "card": {
                            "width": "85%",
                            "height": "300px",
                            "margin-top": "0px",
                        },
                        'title': {
                            'font-family': "Georgia Pro Light, Georgia, serif;",
                            'font-weight': '100'
                        },
                        "filter": {
                            "background-color": "rgba(0, 0, 0, .45)"
                        }
                    }
                )
            

            with col3:
                st.header('Top suggestions')
                # if new recipe, generate summary and save results
                if isinstance(most_helpful_comments, list):
                    suggestions = recipe_suggestions(recipe_name, most_helpful_comments)
                    d_tmp = {
                        'url': st.session_state.recipe_url,
                        'recipe_name': recipe_name,
                        'img_url': img_url,
                        'suggestions': suggestions
                    }
                    st.session_state.df = st.session_state.df._append(d_tmp, ignore_index=True)
                    st.session_state.df.to_csv('nyt_recipes.tsv', sep='\t', index=False)
                st.write(suggestions)
