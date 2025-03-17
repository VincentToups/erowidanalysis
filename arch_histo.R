library(tidyverse);

raw <- read_csv("derived_data/experience_data.csv");
doses <- read_csv("derived_data/doses_data.csv");

pure_experiences <- doses %>% group_by(experience_id) %>% summarize(substances = paste(unique(substance),collapse=", ")) %>% ungroup() %>% filter(substances %in% c("DMT", "Salvia divinorum"));

archetypes <- read_csv("derived_data/archetypes.csv") %>% filter(experience_id %in% pure_experiences$experience_id) %>% inner_join(pure_experiences, by="experience_id");

ps <- archetypes %>% group_by(substances) %>% mutate(n=length(archetype)) %>% ungroup() %>%
    group_by(archetype, n, substances) %>% summarize(p=length(n)/n[[1]]);

order <- archetypes %>% group_by(archetype) %>% tally() %>% arrange(desc(n));
ps <- ps %>% mutate(archetype=factor(archetype, levels=order$archetype));

# Base proportion plot
plot1 <- ggplot(ps, aes(archetype, p)) +
    geom_bar(aes(fill = substances), position = "dodge", stat = "identity") +
    theme_minimal(base_size = 14) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    labs(x = "Archetype", y = "Proportion", fill = "Substances") +
    scale_y_continuous(expand = expansion(mult = c(0, 0.1)))

# Reshape data to wide format for comparison
ps_wide <- ps %>% ungroup() %>% select(-n) %>%
  pivot_wider(names_from = substances, values_from = p, values_fill = list(p = 0)) %>%
  mutate(diff = `Salvia divinorum` - DMT)

# Diverging bar plot
plot2 <- ggplot(ps_wide, aes(x = factor(archetype, levels = order$archetype), y = diff, fill = diff > 0)) +
  geom_bar(stat = "identity") +
  theme_minimal(base_size = 14) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_fill_manual(values = c("salmon","medium turquoise"), labels = c( "DMT", "Salvia divinorum")) +
  labs(x = "Archetype", y = "Proportion Difference (Salvia - DMT)", fill = "Higher in")

# Arrange plots in a single pane
g <- gridExtra::grid.arrange(plot1, plot2, ncol = 1, top = grid::textGrob("Comparison of Archetype Proportions", gp = grid::gpar(fontsize = 16, fontface = "bold")))

system2("mkdir",c("-p","figures"))

ggsave("figures/archetype_histogram.png",plot=g);

