import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = '/api';  // Simplified as we're serving from same origin

function MathChallenge() {
    const [problem, setProblem] = useState(null);
    const [userAnswer, setUserAnswer] = useState('');
    const [feedback, setFeedback] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showExplanation, setShowExplanation] = useState(false);

    // Format problem type for display
    const formatProblemType = (type) => {
        if (!type) return 'Math';
        return type.split(' ').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    // Format explanation with visual step separators
    const formatExplanation = (explanation) => {
        if (!explanation) return '';
        // Split by numbered steps
        const steps = explanation.split(/(?=\n\d+\.)/);
        return steps.map((step, index) => {
            const trimmed = step.trim();
            if (trimmed) {
                return (
                    <div key={index} className="mb-3 pb-3 border-b border-gray-200 last:border-b-0">
                        <p className="text-gray-800">{trimmed}</p>
                    </div>
                );
            }
            return null;
        }).filter(Boolean);
    };

    const fetchNewProblem = async () => {
        setLoading(true);
        console.log('Fetching from:', API_URL);
        try {
            const response = await axios.get(`${API_URL}/problem`);
            console.log('Response:', response.data);
            setProblem(response.data);
            setUserAnswer('');
            setFeedback(null);
            setShowExplanation(false);
        } catch (error) {
            console.error('Error details:', error.message);
            console.error('API URL used:', API_URL);
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
        <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-6 text-center">Math Challenge</h1>

            {loading ? (
                <div className="text-center">Loading...</div>
            ) : problem ? (
                <div className="space-y-4">
                    {/* Difficulty Indicator */}
                    <div className="flex items-center justify-center gap-2 mb-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                            {formatProblemType(problem.problem_type)}
                        </span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                            {problem.num_steps} {problem.num_steps === 1 ? 'step' : 'steps'}
                        </span>
                        {problem.theme && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                                {problem.theme}
                            </span>
                        )}
                    </div>

                    <div className="text-xl text-center font-semibold">
                        {problem.question}
                    </div>

                    {/* Only show input if user hasn't given up (viewed explanation) */}
                    {!showExplanation && (
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
                    )}

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
                                <div className="p-4 bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg border border-gray-200">
                                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                                        <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        Step-by-Step Solution
                                    </h3>
                                    <div className="space-y-2">
                                        {formatExplanation(feedback.explanation)}
                                    </div>
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