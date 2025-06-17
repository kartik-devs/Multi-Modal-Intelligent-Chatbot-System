# Machine Learning: Comprehensive Notes

## 1. Data Representation and Modeling Framework

### Data Structure
- Input features: X = [X₁, X₂, ..., Xₙ] (feature vector with n features)
- Output/target variable: Y (can be binary for classification or real-valued for regression)
- Functional mapping: f: X → Y transforms inputs to outputs
- Probabilistic view: p(Y|X) represents conditional probability distribution

### Data Types
- For binary classification: Y is binary (typically 0/1)
- For regression: Y ∈ ℝ (real values)

## 2. Model Types and Functional Forms

### Binary Classification (Logistic Regression)
- **Probability model**: p(Y=1|X) = 1/(1+e⁻ᶻ)
- **Linear predictor**: Z = Σᵢ₌₀ⁿ βᵢXᵢ where X₀=1 (bias term)
- **Parameters**: n+1 parameters (β₀, β₁, ..., βₙ)
- **Sigmoid/logistic function**: Maps linear predictor to probability [0,1]
- **Decision boundary**: Created where p(Y=1|X) = 0.5

### Linear Regression
- **Model**: p(Y|X) = β₀ + β₁X₁ + ... + βₙXₙ + N(0,σ)
- **Mean function**: μY|X = β₀ + β₁X₁ + ... + βₙXₙ
- **Error term**: N(0,σ) represents Gaussian noise (model uncertainty)
- **Parameters**: β values represent feature weights
- **Interpretation**: Each βᵢ represents change in Y for unit change in Xᵢ

## 3. Cost Functions and Maximum Likelihood Estimation

### Linear Regression Cost Function
- **Mean Squared Error**: C = Σᵢ₌₁ᵐ (yᵢ - f(xᵢ;β))²
- **Optimization objective**: β* = argmin C
- **m**: Number of observations/data points
- **Intuition**: Minimizes squared vertical distances between predictions and actual values

### Logistic Regression Cost Function (Log-Likelihood)
- **Log-likelihood**: C = Σᵢ₌₁ᵐ [yᵢ log θₓ - (1-yᵢ) log(1-θₓ)]
- **Optimization objective**: β* = argmax C
- **Probability**: θₓ = 1/(1+e⁻ᶻˣ), where Zₓ = Σᵢ₌₀ⁿ βᵢXᵢ
- **Intuition**: Maximizes probability of observing the data given the model

## 4. Heuristic Search Algorithms

### Core Concepts of Heuristic Search
- Optimization techniques to efficiently navigate parameter spaces
- Find optimal/near-optimal solutions when exhaustive search is impractical
- Used to find parameters (β*) that minimize or maximize cost functions

### Gradient-Based Methods
- **Fundamental principle**: Move in direction of steepest descent of cost function
- **Update rule**: β⁽ᵗ⁺¹⁾ = β⁽ᵗ⁾ - η∇C(β⁽ᵗ⁾)
  - β⁽ᵗ⁾: Parameters at iteration t
  - η: Learning rate (step size)
  - ∇C: Gradient of cost function
- **Convergence criterion**: ||∇C|| < ε (small threshold)
- **Stopping condition**: ∂C/∂βᵢ = 0 for all i

### Greedy Search Strategies
- **Greedy approach**: Make locally optimal choices at each step
- **Direction selection**: Choose direction giving immediate improvement
- **Step size determination**: Fixed or adaptive based on cost function behavior
- **Parameter update**: β⁽ᵗ⁺¹⁾ = β⁽ᵗ⁾ + δ[direction]

### Dealing with Local Optima
- **Local minimum**: Point where cost function is lower than all nearby points
- **Global minimum**: Lowest possible value of cost function
- **Problem**: Gradient methods can get trapped in local minima

### Strategies to Overcome Local Minima
1. **Multiple starting points**: Initialize from different positions
2. **Momentum**: Adds fraction of previous update to current update
3. **Adaptive step sizes**: Adjust learning rate based on gradient behavior

## 5. Gradient Descent Optimization

### Basic Concept
- Iterative optimization algorithm for finding minimum of differentiable functions
- Moves in the direction of steepest descent (negative gradient)
- Foundation for training many ML models, especially neural networks

### Mathematical Formulation
- **Objective**: Find parameters θ that minimize cost function J(θ)
- **Update rule**: θ := θ - α∇J(θ)
  - α: Learning rate (step size)
  - ∇J(θ): Gradient of cost function

### Linear Regression with Gradient Descent
- **Linear Model**: y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε
- **Matrix form**: y = Xβ + ε
- **Cost Function**: J(β) = (1/2m)||Xβ - y||²
- **Gradient**: ∇J(β) = (1/m)Xᵀ(Xβ - y)

### Matrix Operations
1. Compute predictions: ŷ = Xβ
2. Calculate errors: e = ŷ - y
3. Compute gradient: ∇J(β) = (1/m)Xᵀe
4. Update parameters: β := β - α∇J(β)

### Variants of Gradient Descent
- **Batch Gradient Descent**: Uses entire dataset for each update
- **Stochastic Gradient Descent (SGD)**: Updates using single data point
- **Mini-batch Gradient Descent**: Updates using small random subsets

### Learning Rate Selection
- Too large: May overshoot or diverge
- Too small: Slow convergence
- Adaptive learning rates can help

### Convergence Criteria
- Gradient magnitude below threshold: ||∇J(β)|| < ε
- Change in parameters below threshold: ||βⁿᵉʷ - βᵒˡᵈ|| < ε
- Maximum iterations reached

## 6. Advanced Gradient-Based Optimizers

### Momentum
- **Formula**: v(t+1) = γv(t) + η∇J(θ)
              θ(t+1) = θ(t) - v(t+1)
- **Benefits**: Accelerates convergence, overcomes small local minima
- **Typical γ values**: 0.9 to 0.99

### Nesterov Accelerated Gradient (NAG)
- **Formula**: v(t+1) = γv(t) + η∇J(θ - γv(t))
              θ(t+1) = θ(t) - v(t+1)
- **Advantage**: Looks ahead to where parameters will be

### AdaGrad
- **Adaptive learning rates per parameter**
- **Formula**: θ(t+1) = θ(t) - η/√(G(t) + ε) * ∇J(θ)
- **Benefit**: Works well for sparse features
- **Limitation**: Learning rate diminishes too quickly

### RMSProp
- **Formula**: E[g²](t) = ρE[g²](t-1) + (1-ρ)(∇J(θ))²
              θ(t+1) = θ(t) - η/√(E[g²](t) + ε) * ∇J(θ)
- **Advantage**: Prevents learning rate decay problem of AdaGrad
- **Typical ρ value**: 0.9

### Adam (Adaptive Moment Estimation)
- **Combines momentum and RMSProp**
- **Formula**: 
  - m(t) = β₁m(t-1) + (1-β₁)∇J(θ)  (First moment)
  - v(t) = β₂v(t-1) + (1-β₂)(∇J(θ))²  (Second moment)
  - m̂(t) = m(t)/(1-β₁ᵗ)  (Bias correction)
  - v̂(t) = v(t)/(1-β₂ᵗ)  (Bias correction)
  - θ(t+1) = θ(t) - η * m̂(t)/√(v̂(t) + ε)
- **Default values**: β₁=0.9, β₂=0.999, ε=10⁻⁸

## 7. Regularization Techniques

### Overfitting Problem
- Complex models may fit training data too closely
- Capture noise rather than underlying pattern
- Poor generalization to new data

### L2 Regularization (Ridge)
- **Cost function**: J(β) = MSE + λ∑ᵢ₌₁ⁿβᵢ²
- **Gradient**: ∇J(β) = (1/m)Xᵀ(Xβ - y) + 2λβ
- **Effect**: Shrinks parameters toward zero
- **Geometric interpretation**: Circular constraint region
- **Parameter behavior**: Reduces magnitude but rarely to exactly zero

### L1 Regularization (Lasso)
- **Cost function**: J(β) = MSE + λ∑ᵢ₌₁ⁿ|βᵢ|
- **Gradient**: ∇J(β) = (1/m)Xᵀ(Xβ - y) + λ·sign(β)
- **Effect**: Forces some parameters exactly to zero (feature selection)
- **Geometric interpretation**: Diamond-shaped constraint region

### Hyperparameter λ
- Controls regularization strength
- λ > 0 (must be positive)
- Larger λ means stronger regularization
- Optimal value typically found through cross-validation

## 8. Model Complexity and Fitting

### Underfitting
- **Symptoms**: High bias, model too simple to capture patterns
- **Example**: Using linear model for non-linear data
- **Performance**: Poor on both training and test data
- **Visual**: Straight line trying to fit curved data

### Overfitting
- **Symptoms**: High variance, model captures noise in training data
- **Example**: High-degree polynomial models
- **Performance**: Excellent on training data, poor on test data
- **Visual**: Complex curve passing through every data point

### Polynomial Regression
- **Model extension**: Y = β₀ + β₁X + β₂X² + ... + βₙXⁿ + N(0,σ)
- **Flexibility**: Higher-order terms allow fitting more complex patterns
- **Trade-off**: More flexibility increases risk of overfitting

### Bias-Variance Tradeoff
- **Bias**: Error from simplified model assumptions
- **Variance**: Error from sensitivity to fluctuations in training data
- **Goal**: Find optimal model complexity that balances bias and variance

## 9. Hyperparameter Tuning Methods

### Random Search
- **Process**: Randomly sample hyperparameters from defined distributions
- **Advantages**:
  - More efficient than grid search
  - Better coverage of parameter space
  - Easily parallelizable

### Genetic Algorithms
- **Process**:
  1. Initialize population of hyperparameter configurations
  2. Evaluate fitness (model performance) of each configuration
  3. Select best performers as parents
  4. Create offspring through crossover and mutation
  5. Replace old population with new generation
  6. Repeat until convergence or iteration limit

### Simulated Annealing
- **Process**:
  1. Start with initial hyperparameter configuration
  2. Set initial high "temperature"
  3. Generate neighbor configuration
  4. Accept if better
  5. Accept worse solutions with probability p = e^(-ΔE/T)
  6. Gradually reduce temperature T

### Bayesian Optimization
- **Approach**: Build probabilistic model of objective function
- **Process**:
  1. Build surrogate model (often Gaussian Process)
  2. Use acquisition function to select next point to evaluate
  3. Update model with new observation
  4. Repeat until budget exhausted

## 10. Feature Selection Methods

### Filter Methods
- **Approach**: Select features independent of learning algorithm
- **Techniques**:
  - Correlation-based selection
  - Mutual information
  - Chi-square test
- **Advantages**: Fast, scalable, independent of model

### Wrapper Methods
- **Approach**: Use model performance to evaluate feature subsets
- **Techniques**:
  - Forward selection
  - Backward elimination
  - Recursive feature elimination
- **Advantages**: Considers feature interactions, optimized for specific model

### Embedded Methods
- **Approach**: Feature selection during model training
- **Techniques**:
  - L1 regularization (Lasso)
  - Decision tree importance
  - Gradient boosting importance
- **Advantages**: Computationally efficient, considers model structure 