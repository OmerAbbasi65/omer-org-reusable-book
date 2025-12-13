import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const FeatureList = [
  {
    title: '🤖 AI-Powered Robotics',
    description:
      'Explore the integration of artificial intelligence with physical robotics systems, creating intelligent machines that can perceive, learn, and interact with the world.',
  },
  {
    title: '🦾 Humanoid Systems',
    description:
      'Deep dive into humanoid robot design, biomechanics, and the challenges of creating machines that move and behave like humans.',
  },
  {
    title: '🧠 Machine Learning',
    description:
      'Understand how machine learning algorithms enable robots to adapt, improve, and make decisions in complex real-world environments.',
  },
  {
    title: '⚡ Real-Time Control',
    description:
      'Learn about the control systems and algorithms that enable precise, real-time movement and interaction in robotic systems.',
  },
  {
    title: '🔬 Research & Innovation',
    description:
      'Stay updated with the latest research, breakthroughs, and innovations in the field of physical AI and humanoid robotics.',
  },
  {
    title: '🌐 Ethical Considerations',
    description:
      'Examine the ethical implications, societal impact, and responsible development of intelligent robotic systems.',
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4', styles.feature)}>
      <div className={styles.featureCard}>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroBanner}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroText}>
            <Heading as="h1" className={styles.heroTitle}>
              {siteConfig.title}
            </Heading>
            <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
            <div className={styles.buttons}>
              <Link
                className="button button--primary button--lg"
                to="/docs/01-introduction">
                Start Reading
              </Link>
              <Link
                className="button button--secondary button--lg"
                to="/docs/intro"
                style={{marginLeft: '1rem'}}>
                View Documentation
              </Link>
            </div>
          </div>
          <div className={styles.heroImage}>
            <div className={styles.bookCover}>
              <div className={styles.bookCoverInner}>
                <div className={styles.bookCoverTitle}>Physical AI</div>
                <div className={styles.bookCoverSubtitle}>& Humanoid Robotics</div>
                <div className={styles.bookCoverIcon}>🤖</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.featuresHeader}>
          <Heading as="h2">What You'll Learn</Heading>
          <p>Comprehensive coverage of Physical AI and Humanoid Robotics</p>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="Explore the world of Physical AI and Humanoid Robotics with this comprehensive book.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <section className={styles.ctaSection}>
          <div className="container">
            <div className={styles.ctaContent}>
              <Heading as="h2">Ready to Begin?</Heading>
              <p>
                Start your journey into the fascinating world of Physical AI and Humanoid Robotics.
                This comprehensive book covers everything from fundamental concepts to advanced applications.
              </p>
              <Link
                className="button button--primary button--lg"
                to="/docs/01-introduction">
                Start Reading Now
              </Link>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
