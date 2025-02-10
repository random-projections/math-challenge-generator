import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://math-challenge-gen-backend-production.up.railway.app';

function MathChallenge() {
    const [problem, setProblem] = useState(null);
    const [userAnswer, setUserAnswer] = useState('');
    const [feedback, setFeedback] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showExplanation, setShowExplanation] = useState(false);

    const fetchNewProblem = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/problem`);
            setProblem(response.data);
            setUserAnswer('');
            setFeedback(null);
        } catch (error) {
            console.error('Error details:', error.message);
            if (error.response) {
                console.error('Response data:', error.response.data);
                console.error('Response status:', error.response.status);
            } else if (error.request) {
                console.error('No response received');
            }
        }
        setLoading(false);
    };

    const checkAnswer = async () => {
        if (!userAnswer) return;

        try {
            const response = await axios.post(`${API_URL}/check_answer`, {
                problem_id: problem.problem_id,
                user_answer: parseFloat(userAnswer)
            });

            setFeedback(response.data);
        } catch (error) {
            console.error('Error checking answer:', error);
        }
    };

    useEffect(() => {
        fetchNewProblem();
    }, []);

    return (
        <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-6 text-center">Math Challenge</h1>
            
            {loading ? (
                <div className="text-center">Loading...</div>
            ) : problem ? (
                <div className="space-y-4">
                    <div className="text-xl text-center font-semibold">
                        {problem.question}
                    </div>
                    
                    <div className="flex space-x-2">
                        <input
                            type="number"
                            step="0.01"
                            value={userAnswer}
                            onChange={(e) => setUserAnswer(e.target.value)}
                            className="flex-1 p-2 border rounded"
                            placeholder="Your answer"
                        />
                        <button
                            onClick={checkAnswer}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            Submit
                        </button>
                    </div>

                    {feedback && (
                        <div className="space-y-2">
                            <div className={`p-3 rounded ${feedback.correct ? 'bg-green-100' : 'bg-red-100'}`}>
                                {feedback.correct ? (
                                    <p className="text-green-700">Correct! Well done!</p>
                                ) : (
                                    <p className="text-red-700">
                                        Incorrect. The correct answer was {feedback.correct_answer}.
                                    </p>
                                )}
                            </div>
                            
                            {!feedback.correct && (
                                <button
                                    onClick={() => setShowExplanation(!showExplanation)}
                                    className="w-full px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                                >
                                    {showExplanation ? 'Hide' : 'Show'} Explanation
                                </button>
                            )}
                            
                            {showExplanation && (
                                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">
                                    {feedback.explanation}
                                </div>
                            )}
                        </div>
                    )}

                    <button
                        onClick={fetchNewProblem}
                        className="w-full mt-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                        New Problem
                    </button>
                </div>
            ) : (
                <div className="text-center text-red-500">
                    Error loading problem
                </div>
            )}
        </div>
    );
}

export default MathChallenge; 