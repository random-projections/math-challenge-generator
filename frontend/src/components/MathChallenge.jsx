import React, { useState } from 'react';
import axios from 'axios';

const API_URL = '/api';  // Simplified as we're serving from same origin

function MathChallenge() {
    const [problem, setProblem] = useState(null);
    const [userAnswer, setUserAnswer] = useState('');
    const [feedback, setFeedback] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showExplanation, setShowExplanation] = useState(false);

    // Session tracking
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [sessionStats, setSessionStats] = useState({
        total: 0,
        correct: 0,
        incorrect: 0,
        skipped: 0
    });
    const [showSummary, setShowSummary] = useState(false);

    // Problem queue for pre-fetching
    const [problemQueue, setProblemQueue] = useState([]);

    // Format problem type for display
    const formatProblemType = (type) => {
        if (!type) return 'Math';
        return type.split(' ').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    // Format question text - split into sentences for better readability
    const formatQuestion = (question) => {
        if (!question) return [];
        // Split by sentence endings (. ! ?) but keep the punctuation
        const sentences = question.match(/[^.!?]+[.!?]+/g) || [question];
        return sentences.map(s => s.trim()).filter(s => s.length > 0);
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

    // Fetch a single problem and add to queue
    const fetchProblemToQueue = async () => {
        try {
            const response = await axios.get(`${API_URL}/problem`);
            setProblemQueue(prev => [...prev, response.data]);
        } catch (error) {
            console.error('Error fetching problem to queue:', error);
        }
    };

    // Pre-fetch multiple problems
    const prefetchProblems = async (count = 5) => {
        const promises = [];
        for (let i = 0; i < count; i++) {
            promises.push(fetchProblemToQueue());
        }
        await Promise.all(promises);
    };

    // Get next problem from queue or fetch if empty
    const fetchNewProblem = async () => {
        setLoading(true);
        try {
            if (problemQueue.length > 0) {
                // Use problem from queue
                const nextProblem = problemQueue[0];
                setProblem(nextProblem);
                setProblemQueue(prev => prev.slice(1));

                // Refill queue if running low
                if (problemQueue.length < 3) {
                    fetchProblemToQueue();
                }
            } else {
                // Queue empty, fetch directly
                const response = await axios.get(`${API_URL}/problem`);
                setProblem(response.data);
            }

            setUserAnswer('');
            setFeedback(null);
            setShowExplanation(false);
        } catch (error) {
            console.error('Error fetching problem:', error);
        }
        setLoading(false);
    };

    const startSession = async () => {
        setIsSessionActive(true);
        setShowSummary(false);
        setSessionStats({
            total: 0,
            correct: 0,
            incorrect: 0,
            skipped: 0
        });

        // Fetch first problem immediately to show it
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/problem`);
            setProblem(response.data);
            setUserAnswer('');
            setFeedback(null);
            setShowExplanation(false);
        } catch (error) {
            console.error('Error fetching first problem:', error);
        }
        setLoading(false);

        // Pre-fetch remaining problems in background
        prefetchProblems(4);
    };

    const endSession = () => {
        setIsSessionActive(false);
        setShowSummary(true);
        setProblem(null);
        setFeedback(null);
    };

    const checkAnswer = async () => {
        if (!userAnswer) return;

        try {
            const response = await axios.post(`${API_URL}/check_answer`, {
                problem_id: problem.problem_id,
                user_answer: parseFloat(userAnswer)
            });

            setFeedback(response.data);

            // Update session stats
            if (isSessionActive) {
                setSessionStats(prev => ({
                    ...prev,
                    total: prev.total + 1,
                    correct: prev.correct + (response.data.correct ? 1 : 0),
                    incorrect: prev.incorrect + (response.data.correct ? 0 : 1)
                }));
            }
        } catch (error) {
            console.error('Error checking answer:', error);
        }
    };

    const handleShowExplanation = () => {
        // If user views explanation without answering, count as skipped
        if (isSessionActive && !feedback) {
            setSessionStats(prev => ({
                ...prev,
                total: prev.total + 1,
                skipped: prev.skipped + 1
            }));
        }
        setShowExplanation(true);
    };

    // No initial fetch - problems are fetched when session starts

    const getCelebrationMessage = () => {
        const percentage = sessionStats.total > 0 ? (sessionStats.correct / sessionStats.total) * 100 : 0;

        if (percentage >= 90) {
            return { emoji: "🏆", message: "Outstanding! You're a math superstar!", color: "text-yellow-600" };
        } else if (percentage >= 70) {
            return { emoji: "🎉", message: "Excellent work! You're doing great!", color: "text-green-600" };
        } else if (percentage >= 50) {
            return { emoji: "👍", message: "Good effort! Keep practicing!", color: "text-blue-600" };
        } else {
            return { emoji: "💪", message: "Keep going! Practice makes perfect!", color: "text-purple-600" };
        }
    };

    return (
        <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-lg">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">Math Challenge</h1>

                {isSessionActive && (
                    <div className="flex items-center gap-4">
                        <div className="text-sm">
                            <span className="font-semibold">Score:</span>{' '}
                            <span className="text-green-600">{sessionStats.correct}</span> /{' '}
                            <span className="text-red-600">{sessionStats.incorrect}</span> /{' '}
                            <span className="text-gray-600">{sessionStats.skipped} skipped</span>
                        </div>
                        <button
                            onClick={endSession}
                            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                        >
                            End Session
                        </button>
                    </div>
                )}
            </div>

            {showSummary ? (
                // Summary View
                <div className="text-center space-y-6">
                    <div className="text-6xl">{getCelebrationMessage().emoji}</div>
                    <h2 className={`text-3xl font-bold ${getCelebrationMessage().color}`}>
                        {getCelebrationMessage().message}
                    </h2>

                    <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
                        <div className="bg-green-50 p-4 rounded-lg">
                            <div className="text-3xl font-bold text-green-600">{sessionStats.correct}</div>
                            <div className="text-sm text-gray-600">Correct</div>
                        </div>
                        <div className="bg-red-50 p-4 rounded-lg">
                            <div className="text-3xl font-bold text-red-600">{sessionStats.incorrect}</div>
                            <div className="text-sm text-gray-600">Incorrect</div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <div className="text-3xl font-bold text-gray-600">{sessionStats.skipped}</div>
                            <div className="text-sm text-gray-600">Skipped</div>
                        </div>
                    </div>

                    <div className="bg-blue-50 p-6 rounded-lg max-w-md mx-auto">
                        <div className="text-lg font-semibold mb-2">Total Questions</div>
                        <div className="text-4xl font-bold text-blue-600">{sessionStats.total}</div>
                        {sessionStats.total > 0 && (
                            <div className="mt-2 text-lg">
                                Accuracy: <span className="font-bold">{Math.round((sessionStats.correct / sessionStats.total) * 100)}%</span>
                            </div>
                        )}
                    </div>

                    <button
                        onClick={startSession}
                        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-lg font-semibold"
                    >
                        Start New Session
                    </button>
                </div>
            ) : !isSessionActive ? (
                // Start Session View
                <div className="text-center space-y-6">
                    <div className="text-6xl">🎯</div>
                    <h2 className="text-2xl font-semibold text-gray-700">Ready to practice math?</h2>
                    <p className="text-gray-600">Start a session to track your progress and see how well you do!</p>
                    <button
                        onClick={startSession}
                        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-lg font-semibold"
                    >
                        Start Session
                    </button>
                </div>
            ) : loading ? (
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

                    <div className="text-xl font-semibold space-y-2 text-left max-w-xl mx-auto">
                        {formatQuestion(problem.question).map((sentence, index) => (
                            <div key={index} className="leading-relaxed">
                                {sentence}
                            </div>
                        ))}
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
                                    onClick={handleShowExplanation}
                                    className="w-full px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                                    disabled={showExplanation}
                                >
                                    {showExplanation ? 'Explanation Shown' : 'Show Explanation (Skip)'}
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