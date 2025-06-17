# Machine Learning Notes Repository

A comprehensive collection of machine learning notes focused on fundamental concepts, algorithms, and optimization techniques.

## Table of Contents

1. [Regression and Classification Models](#regression-and-classification-models)
2. [Cost Functions and Maximum Likelihood](#cost-functions-and-maximum-likelihood)
3. [Heuristic Search Algorithms](#heuristic-search-algorithms)
4. [Gradient Descent Optimization](#gradient-descent-optimization)
5. [Regularization Techniques](#regularization-techniques)
6. [Underfitting and Overfitting](#underfitting-and-overfitting)
7. [Neural Network Optimization](#neural-network-optimization)
8. [Hyperparameter Tuning](#hyperparameter-tuning)
9. [Feature Selection](#feature-selection)

## Regression and Classification Models

- **Binary Classification (Logistic Regression)**
  - Probability model: p(Y=1|X) = 1/(1+e⁻ᶻ)
  - Linear predictor: Z = Σᵢ₌₀ⁿ βᵢXᵢ where X₀=1 (bias term)
  - Parameters: n+1 parameters (β₀, β₁, ..., βₙ)

- **Linear Regression**
  - Model: p(Y|X) = β₀ + β₁X₁ + ... + βₙXₙ + N(0,σ)
  - Mean function: μY|X = β₀ + β₁X₁ + ... + βₙXₙ
  - Error term: N(0,σ) represents Gaussian noise

## Cost Functions and Maximum Likelihood

- **Linear Regression Cost (MSE)**
  - C = Σᵢ₌₁ᵐ (yᵢ - f(xᵢ;β))²
  - Optimization: β* = argmin C

- **Logistic Regression Cost (Log-Likelihood)**
  - C = Σᵢ₌₁ᵐ [yᵢ log θₓ - (1-yᵢ) log(1-θₓ)]
  - Optimization: β* = argmax C
  - Probability: θₓ = 1/(1+e⁻ᶻˣ)

## Heuristic Search Algorithms

- **Gradient-Based Methods**
  - Find where ∂C/∂βᵢ = 0
  - Update rule: β⁽ᵗ⁺¹⁾ = β⁽ᵗ⁾ + δ[∇C]

- **Local vs. Global Minima**
  - Challenge: Cost functions may have multiple local minima
  - Convex functions: Have single global minimum
  - Non-convex functions: May require multiple starting points

## Gradient Descent Optimization

- **Basic Update Rule**: θ := θ - α∇J(θ)
  - α: Learning rate (step size)
  - ∇J(θ): Gradient of cost function

- **Matrix Operations**
  1. Compute predictions: ŷ = Xβ
  2. Calculate errors: e = ŷ - y
  3. Compute gradient: ∇J(β) = (1/m)Xᵀe
  4. Update parameters: β := β - α∇J(β)

- **Variants**
  - Batch Gradient Descent: Uses entire dataset
  - Stochastic Gradient Descent: Uses single data point
  - Mini-batch Gradient Descent: Uses small random subsets

## Regularization Techniques

- **L2 Regularization (Ridge)**
  - Cost function: J(β) = MSE + λ∑ᵢ₌₁ⁿβᵢ²
  - Effect: Shrinks parameters toward zero

- **L1 Regularization (Lasso)**
  - Cost function: J(β) = MSE + λ∑ᵢ₌₁ⁿ|βᵢ|
  - Effect: Forces some parameters exactly to zero (feature selection)

## Underfitting and Overfitting

- **Underfitting**
  - High bias, model too simple to capture patterns
  - Poor performance on both training and test data

- **Overfitting**
  - High variance, model captures noise in training data
  - Excellent on training data, poor on test data

## Neural Network Optimization

- **Adam (Adaptive Moment Estimation)**
  - Combines momentum and RMSProp
  - Adaptive learning rates per parameter
  - Default values: β₁=0.9, β₂=0.999, ε=10⁻⁸

- **RMSProp**
  - Prevents learning rate decay problem of AdaGrad
  - Maintains per-parameter learning rates

## Hyperparameter Tuning

- **Random Search**
  - Randomly sample hyperparameters from defined distributions
  - More efficient than grid search

- **Bayesian Optimization**
  - Build probabilistic model of objective function
  - Sample-efficient for expensive evaluations

## Feature Selection

- **Filter Methods**
  - Select features independent of learning algorithm

- **Wrapper Methods**
  - Use model performance to evaluate feature subsets

- **Embedded Methods**
  - Feature selection during model training
  - L1 regularization (Lasso) 