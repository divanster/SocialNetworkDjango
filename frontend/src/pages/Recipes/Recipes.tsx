import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Recipe } from '../../types/Recipe'; // Import the Recipe type

const Recipes: React.FC = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]); // Update the state type
  const [error, setError] = useState<string | null>(null); // Update the error type
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/recipes/');
        setRecipes(response.data.results); // Use the correct data structure
      } catch (err) {
        console.error('Error fetching recipes:', err); // Log any errors
        setError(err instanceof Error ? err.message : 'An error occurred'); // Update the error handling
      } finally {
        setLoading(false);
      }
    };

    fetchRecipes();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      {recipes.length === 0 ? (
        <div>No recipes available</div>
      ) : (
        recipes.map((recipe) => (
          <div key={recipe.id}>
            <h2>{recipe.title}</h2>
            <p>{recipe.description}</p>
            {recipe.image && <img src={recipe.image} alt={recipe.title} />}
          </div>
        ))
      )}
    </div>
  );
};

export default Recipes;
