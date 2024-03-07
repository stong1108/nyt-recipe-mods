# NYT Recipe Modifications
Weekend project that takes a link to a new New York Times Cooking recipe link and outputs the most helpful recipe modifications submitted by users.

[Streamlit App](https://nyt-recipe-mods.streamlit.app/)

## Demo
Input:
```
recipe_url = 'https://cooking.nytimes.com/recipes/1025042-microwave-salmon'
recipe_suggestions(recipe_url)
```

Output:
```
Suggested improvements for Microwave Salmon Recipe
- Use Italian dressing instead of water for added flavor
- Add garlic powder, lemon juice, bay leaf, and thyme for enhanced taste
- Use lime juice to reduce fish odor in the microwave
- Brush the bottom of the dish with olive oil and add white vermouth and fresh herbs for extra flavor
- Use an insta-read thermometer to prevent overcooking
```

## Requirements
- OpenAI API access
- NYT cooking subscription

## Python packages
- `openai`
- `beautifulsoup4`
- `requests`
