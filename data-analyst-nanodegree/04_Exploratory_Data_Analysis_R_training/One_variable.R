reddit <- read.csv('reddit.csv')
table(reddit$employment.status)
summary(reddit)
levels(reddit$age.range)
library(ggplot2)
qplot(data = reddit, x = age.range)
str(reddit)
reddit$age.range <- factor(reddit$age.range, levels = c("Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65 or Above"))
levels(reddit$age.range)

# Exercises

library(ggplot2)
library(tidyr)

men_fat = read.csv2('Indicator_TC male ASM.csv')
head(men_fat)
str(men_fat)
names(men_fat)
colnames(men_fat) <- c('Country', seq(1980, 2008, 1))
tidy_men <- gather(men_fat, year, value, -Country)
tidy_men$year <- as.numeric(tidy_men$year)
tidy_men[tidy_men$Country=='France',]
tidy_men$sex <- factor('men')
head(tidy_men)



women_fat = read.csv2('Indicator_TC female ASM.csv')
colnames(women_fat) <- c('Country', seq(1980, 2008, 1))
names(women_fat)
tidy_women <- gather(women_fat, year, value, -Country)
tidy_women$sex = factor("women")
tidy_women$year <- as.numeric(tidy_women$year)
str(tidy_women)
head(tidy_women)

tidy = rbind(tidy_men, tidy_women)
tidy <- tidy[order(tidy$year),]
head(tidy)
head(tidy[tidy$Country=='France',])

by(tidy$value, tidy$year, summary)

ggplot(aes(x = year, y = value, group=year), data = tidy)+
  geom_boxplot()+
  facet_wrap(~sex)

ggplot(aes(x = year, y = value), data = subset(tidy, tidy$Country=='France'))+
  geom_point(aes(colour=sex))

ggplot(aes(x = year, y = value, group=year), data = tidy)+
  stat_summary(fun.y = median, geom='point')

ggplot(aes(x = year, y = value), data = tidy)+
  stat_summary(fun.y = median, aes(color=sex), geom='point')