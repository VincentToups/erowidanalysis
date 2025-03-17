library(tidyverse)
library(rstan)

# Load data
df <- read_csv("derived_data/archetypes.csv");

expdata <- read_csv("derived_data/experience_data.csv");
expids <- expdata %>%
    group_by(experience_id) %>% tally() %>% filter(n==1);


df <- df %>%
    filter(archetype=="trickster") %>% right_join(expids, by="experience_id") %>%
    mutate(motif_flag = 1*(archetype == "trickster") %>% replace_na(0)) %>%
    inner_join(expdata,by="experience_id") %>%
    select(-experience_account, -exp_id) %>%
    mutate(exp_year=exp_year %>% as.numeric(),
           age=age %>% as.numeric()) %>%
    filter(!is.na(exp_year) & !is.na(age)) %>%
    arrange(exp_year) %>%
    filter(gender %in% c("Male","Female")) %>%
    mutate(gender=1*(gender=="Female") %>% replace_na(0),
           age=scale(age)) %>%
    select(-archetype,-n,-views,-published) %>%
    rename(date=exp_year,
           subject=experience_id);

# Compute p_t: proportion of motif occurrences before each date
df <- df %>%
  arrange(date) %>%
  group_by(date) %>%
  mutate(
    cum_motif = cumsum(lag(motif_flag, default = 0)),
    cum_total = row_number() - 1,
    p_motif = ifelse(cum_total > 0, cum_motif / cum_total, 0)
  ) %>%
  ungroup()

# Encode subjects as numeric
df$subject <- as.numeric(factor(df$subject))

# Prepare data list for Stan
stan_data <- list(
  N = nrow(df),                        # Total number of observations
  S = length(unique(df$subject)),      # Number of subjects
  subj = as.vector(df$subject),        # Subject ID as a vector
  age = as.vector(df$age),             # Standardized age as a vector
  gender = as.vector(df$gender),       # Gender binary as a vector
  p_motif = as.vector(df$p_motif),     # Past prevalence of motif as a vector
  motif_flag = as.vector(df$motif_flag)  # Response variable as a vector
)

fit <- stan(
  file = "model.stan",
  data = stan_data,
  iter = 5000,
  warmup = 1000,
  chains = 4,
  cores = 4
)

print(fit, pars = c("alpha_0", "alpha_1", "alpha_2", "beta_0", "beta_1", "beta_2", "sigma_theta", "sigma_gamma"))

stan_data2 <- list(
  N = nrow(df),                        # Total number of observations
  S = length(unique(df$subject)),      # Number of subjects
  subj = as.vector(df$subject),        # Subject ID as a vector
  p_motif = as.vector(df$p_motif),     # Past prevalence of motif as a vector
  motif_flag = as.vector(df$motif_flag)  # Response variable as a vector
)

fit <- stan(
  file = "simpler_model.stan",
  data = stan_data2,
  iter = 2000,
  warmup = 1000,
  chains = 4,
  cores = 4
)
