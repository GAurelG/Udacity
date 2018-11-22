library(ggplot2)
pf <- read.csv("pseudo_facebook.tsv", sep="\t")

ggplot(aes(x = age, y = friend_count), data = pf) +
  geom_point(alpha=1/20)+
  xlim(13,90)

# use geom_jitter to spread data on each age group
ggplot(aes(x = age, y = friend_count), data = pf) +
  geom_jitter(alpha=1/20)+
  xlim(13,90)

ggplot(aes(x = age, y = friend_count), data = pf) +
  geom_point(alpha=1/20, position=position_jitter(h = 0))+
  xlim(13,90)+
  coord_trans(y = 'sqrt')

# friend initiated vs age:
ggplot(aes(x=age, y=friendships_initiated), data = pf)+
  geom_point(alpha=1/20, position=position_jitter(h=0))+
  xlim(13,90)+
  coord_trans(y='sqrt')+
  labs(title = 'friendship intiated vs age')



# conditionnal mean
#install.packages("dplyr")
library(dplyr)
# example of dplyr functions:
'''
filter()
group_by()
mutate()
arrange()
'''
ages_groups <- group_by(pf, age)
pf.fc_by_age <- summarise(ages_groups,
          friend_count_mean = mean(friend_count),
          friend_count_median = median(friend_count),
          n = n())
pf.fc_by_age <- arrange(pf.fc_by_age, age)
head(pf.fc_by_age)

ggplot(aes(x = age, y = friend_count_mean), data = pf.fc_by_age)+
  geom_line()
  
# Overlaying plots:

ggplot(aes(x = age, y = friend_count), data = pf) +
  geom_point(alpha=1/20, position=position_jitter(h = 0), color='orange')+
  coord_cartesian(xlim = c(13,90), ylim = c(0,1000))+
  #coord_trans(y = 'sqrt')+
  geom_line(stat = 'summary',fun.y = mean)+
  geom_line(stat = 'summary', fun.y = quantile, fun.args = list(probs = .1), 
            linetype = 2, color = 'blue')+
  geom_line(stat = 'summary', fun.y = quantile, fun.args = list(probs = .9), 
            linetype = 2, color = 'blue')+
  geom_line(stat = 'summary', fun.y = median, color = 'red')

# correletion between friend count and age:
cor(pf$age, pf$friend_count)
cor.test(pf$age, pf$friend_count, method = 'pearson')
with(pf, cor.test(age, friend_count, method = 'pearson'))

# correlation on subset:
with(subset(pf, age<=70), cor.test(age, friend_count, method = 'pearson'))

# Create a scatterplot of likes_received (y)
# vs. www_likes_received (x). Use any of the
# techniques that you've learned so far to
# modify the plot.

ggplot(aes(x=likes_received, y=www_likes_received), data = pf)+
  geom_point(alpha=1/5)+
  xlim(0, quantile(pf$likes_received, .95))+
  ylim(0, quantile(pf$www_likes_received, 0.95))+
  geom_smooth(method = 'lm', color = 'red')

with(pf, cor.test(www_likes_received, likes_received))
#install.packages('alr3')
library(alr3)
data("Mitchell")

# Create a scatterplot of temperature (Temp)
# vs. months (Month).
ggplot(aes(x = Month, y = Temp), data = Mitchell)+
  geom_point()
cor.test(Mitchell$Month, Mitchell$Temp)

#make a plot overlayin only 12 month
ggplot(aes(x=(Month%%12), y=Temp), data = Mitchell)+
  geom_point()


names(pf)
head(pf$dob_month)
# Create a column of date of birth accounting for month:
pf$age_with_months <-pf$age + (1 - pf$dob_month / 12)

# Create a new data frame called
# pf.fc_by_age_months that contains
# the mean friend count, the median friend
# count, and the number of users in each
# group of age_with_months. The rows of the
# data framed should be arranged in increasing
# order by the age_with_months variable.

gp <- group_by(pf, age_with_months)
pf.fc_by_age_months <- summarise(gp,
                                 mean_friend_count = mean(friend_count),
                                 median_friend_count = median(friend_count),
                                 n = n())
pf.fc_by_age_months <- arrange(pf.fc_by_age_months, age_with_months)
head(pf.fc_by_age_months)

# plot with age < 71

ggplot(aes(x = age_with_months, y = mean_friend_count), data = pf.fc_by_age_months)+
  geom_line()+
  xlim(c(0, 71))





