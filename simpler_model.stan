data {
  int<lower=1> N;       // Number of observations
  int<lower=1> S;       // Number of subjects
  int<lower=1, upper=S> subj[N]; // Subject IDs
  real<lower=0, upper=1> p_motif[N]; // Proportion of past reports
  int<lower=0, upper=1> motif_flag[N]; // Observed motif occurrences
}

parameters {
  real alpha_0;               // Baseline endogenous probability
  real beta_0;                // Baseline sensitivity to p_motif
  real<lower=0> sigma_theta;  // Subject variation in theta
  real<lower=0> sigma_gamma;  // Subject variation in gamma
  vector[S] theta_raw;        // Subject-level random effect for theta
  vector[S] gamma_raw;        // Subject-level random effect for gamma
}

transformed parameters {
  vector[S] theta;
  vector[S] gamma;

  for (s in 1:S) {
    theta[s] = alpha_0 + sigma_theta * theta_raw[s];
    gamma[s] = beta_0 + sigma_gamma * gamma_raw[s];
  }
}

model {
  // Priors
  alpha_0 ~ normal(0, 1);
  beta_0 ~ normal(0, 1);
  sigma_theta ~ normal(0, 1);
  sigma_gamma ~ normal(0, 1);

  theta_raw ~ normal(0, 1);
  gamma_raw ~ normal(0, 1);

  // Likelihood
  for (n in 1:N) {
    real lambda_n = inv_logit(gamma[subj[n]] * p_motif[n]); // Social influence
    real theta_n = inv_logit(theta[subj[n]]); // Endogenous probability
    real prob_motif = 1 - (1 - theta_n) * (1 - lambda_n); // Combined probability
    motif_flag[n] ~ bernoulli(prob_motif);
  }
}
