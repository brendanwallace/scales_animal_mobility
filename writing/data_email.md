Hi ?,

We're writing to ask whether you'd be open to sharing your [data] with us for a project on nested scales in animal mobility.

## Project info
*This recent paper* addresses a contradiction in the human mobility literature between an empirical scale-free power law distribution of travel distances (see [?], [?]) and the intuitively obvious way that anthropic transportation options operate at distinct scales. They infer, from a human GPS trace, a nested set of heirarchical containers (e.g. a single building, within a neighborhood, within a city, etc.) with associated probabilities of transitioning between heirarchical levels; but show that these transition probabilities still reproduce a distribution that matches the empirical power law shape.

The authors' model is open source, and they've expressed interest in our group applying the model to animal movement traces to see whether we can produce a similar result. So we're reaching out to folks who might have 

## Data requirements

- High temporal-granularity GPS tracks would be best
- track a single individual over at least several days



<!-- 

# Chapter 3 - Scales of Animal Mobility 

## Introduction

A large body of research tries to mathematically aggregate patterns in human movement. An early finding shows that distances traveled by paper currency are power-law distributed {[}14{]}. Another result shows  that the number of people moving between cities is proportional to the sizes of both cities, divided by the squared distance between them --- this is known as the the gravity model \cite{zipf1946p1} \cite{barthelemy2011spatial}\cite{erlander1990gravity}. The ``radiation'' further refines the picture by considering intervening opportunities between cities and places \cite{simini2012universal}. The state of the art model explains a power-law distribution of travel distances by considering preferential return to previously explored locations \cite{song2010modelling}.

Empirical data support the finding that, over a large range, the frequency of human trips of a certain distance obeys a power law distribution with trips of longer distances less frequent. However, this result, specifically that the distribution should be smooth and follow a power law, is at odds with a common sense and a psychological view of how people decide when and where to travel {[}2{]}. Psychology tells us that specific locations are important, and that people think about space and distances in a scaled, hierarchical way. We should see scales in the distribution of trip frequencies, but power laws are ``scale-free''.  \cite{alessandretti2020scales} resolve this contradiction with a model that uncovers scales implicit in movement data sets. They show how the aggregation of movement lengths drawn from different scales aggregate into a ``scale-free'' power-law distribution. Their model produces, for a given individual, a nested hierarchy of ``scales'' (geographical levels such as region, city, neighborhood, etc.) into which all locations that an individual visits fit and is described in more detail in Methods. The model finds a consistent number of scales in movement --- on average 4 --- as well as noticeable differences in the number of scales when broken down by gender, and country, which may be used as diagnostics for gender inequities.

Researchers have similarly debated whether animal movements contain scale-free distributions of travel distances. Researchers in 1996 studied the flight paths of albatrosses and determined that their movements follow a L\'evy flight pattern such that their step lengths obey a scale-free distribution\cite{viswanathan1996levy}. This pattern was found again in jackals \cite{atkinson2002scalefree}, and spider monkeys \cite{ramos-fernandez2004levy}, and shown to be optimal for predatory exploration under various environmental conditions \cite{reynolds2009levy} \cite{humphries2010environmental}. Other researchers dispute the finding that animal travel distances follow a scale-free distribution at all \cite{edwards2007revisiting} \cite{benhamou2007how} \cite{edwards2011overturning}.

This chapter seeks to see whether hierarchical scales in movement exist in behavior in other species - i.e., to investigate the scales of animal mobility. It will consider behavior splits such as forager vs. predator, migratory vs nonmigratory, etc. and see whether the model can identify distinct scales in their movement behavior.

## Objectives

\begin{enumerate}
\def\labelenumi{\arabic{enumi}.}
\tightlist
\item Identify animal tracks to use
\item Identify scales in animal movement
\item Analysis
\end{enumerate}

## Methodology

### Identify a suitable set of animal track data sets

Animal tracks are available for hundreds of different species and sources from \href{movebank.org}{Movebank}. Many sets of tracks are available for multiple individuals of the same species using high resolution GPS data. From this database, we will identify at least 10 groups of animals of interest to analyze.

We will try to identify species that are either:

\begin{itemize}
\tightlist
\item predators
\item foragers, or
\item herbivores
\end{itemize}

Additionally, we may consider species known to be territorial as well as non-territorial species; migratory, nomadic, and stationary species; aerial, aquatic and terrestrial species; etc.

Animal tracks must be from GPS tags and have sufficiently high temporal resolution (at least several samples per hour).

\subsubsection{Identify scales in animal
movement}\label{identify-scales-in-animal-movement}

To identify scales in the movement of our chosen animals, we need to first process GPS tracks into ``stops'' and ``trips''. We will use the infostop library (\url{https://github.com/ulfaslak/infostop} – a package for detecting stop locations in GPS trajectories) to accomplish this. We will validate the approach by choosing a sample of GPS tracks and identifying stops and trips by hand and comparing against the output of the infostop program.

We will then apply the \textit{Scales-of-human-mobility} model\cite{alessandretti2020scales} to the processed tracks to produce, for each animal, a nested set of locations and transition probabilities.

### Analysis

We will validate the resulting model output by comparing synthetic traces to a validation set of tracks using the following metrics:

\begin{itemize}
\tightlist
\item   radius of gyration
\item   probability distribution of trip lengths
\item   frequency of location visitation
\item   entropy
\end{itemize}

## Results

The \textit{Scales-of-human-mobility} model produces a set of nested
locations and containers at different scales for one individual's
movement: at the level of building, neighborhood, city, region, etc.
People have on average 4 meaningful scales to their movement.

We plan to produce a similar result for our chosen animals: a histogram
of the number of scales that characterize their movement and a
histogram of the average amount of time spent in containers at different
levels. We will then evaluate, by regression, correlations between the
behavioral features identified for each species and characteristics of
the distribution of their scales of movement.

## Interpretation

Do animals other than humans organize their movements in space into hierarchical scales? If they do, we may learn something about our own behavior by putting it in its larger ecological context. Foragers and predators have markedly different patterns in their movements; and humans may fit neatly into one category. Territorial animals may be categorized by a certain distribution pattern distinct from non-territorial animals, and again the agreement between human patterns and these categories may be telling.

Conversely, if other animals don't organize their movements this way there is still something to learn. If the Scales of Human Mobility model is a poor fit for animal movement in general, this suggests that hierarchical patterns are a unique aspect of human behavior and our relationship with our built environment.
 -->