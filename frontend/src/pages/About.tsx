import { motion } from "framer-motion";
import { ExternalLink, Award, Users, Target, Eye } from "lucide-react";
import SEO from "@/components/SEO";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { containerVariants, itemVariants } from "@/components/PageTransition";

export default function About() {
  return (
    <motion.div
      className="container py-10"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <SEO 
        title="About Us | Alex Designs" 
        description="Learn about Alex Designs, our vision, and our CEO Muhammad Aboelhamd's architectural expertise." 
        canonical="/about" 
      />

      {/* Hero Section */}
      <motion.section className="text-center mb-16" variants={itemVariants}>
        <h1 className="font-heading text-4xl md:text-5xl mb-6">About Alex Designs</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
          We create thoughtfully designed spaces that seamlessly blend form and function, 
          emphasizing sustainable design, natural light integration, and timeless minimalist aesthetics.
        </p>
      </motion.section>

      {/* CEO Section */}
      <motion.section className="mb-16" variants={itemVariants}>
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <motion.div variants={itemVariants}>
              <Badge variant="secondary" className="mb-4">CEO & Founder</Badge>
              <h2 className="font-heading text-3xl mb-4">Muhammad Aboelhamd</h2>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                A forward-thinking architect passionate about architectural excellence, Muhammad leads Alex Designs 
                with a Master's Degree in Architecture and RIAI Post-Graduate Membership. Based between Alexandria, Egypt, 
                and international projects, he brings global expertise to every design.
              </p>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-center gap-3">
                  <Award className="h-5 w-5 text-primary" />
                  <span>Master Degree in Architecture</span>
                </div>
                <div className="flex items-center gap-3">
                  <Award className="h-5 w-5 text-primary" />
                  <span>RIAI Post-Graduate Membership</span>
                </div>
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-primary" />
                  <span>CEO | Architect | Interior Designer | BIM Coordinator</span>
                </div>
              </div>

              <Button asChild size="lg">
                <a 
                  href="https://www.behance.net/mohamedaboelhamd" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2"
                >
                  View Portfolio on Behance
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            </motion.div>
          </div>

          <motion.div variants={itemVariants}>
            <Card className="p-6">
              <CardContent className="p-0">
                <div className="grid grid-cols-2 gap-6 text-center">
                  <div>
                    <div className="text-3xl font-bold text-primary mb-2">86K+</div>
                    <div className="text-sm text-muted-foreground">Project Views</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-primary mb-2">14K+</div>
                    <div className="text-sm text-muted-foreground">Appreciations</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-primary mb-2">4.7K+</div>
                    <div className="text-sm text-muted-foreground">Followers</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-primary mb-2">10+</div>
                    <div className="text-sm text-muted-foreground">Years Experience</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </motion.section>

      {/* Values Section */}
      <motion.section className="mb-16" variants={itemVariants}>
        <div className="text-center mb-12">
          <h2 className="font-heading text-3xl mb-4">Our Values</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            The principles that guide every design decision and client relationship.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <motion.div variants={itemVariants}>
            <Card className="text-center p-6 h-full">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Eye className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Vision</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Creating timeless architectural solutions that enhance the human experience 
                  through thoughtful design and innovation.
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="text-center p-6 h-full">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Target className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Mission</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  To deliver exceptional architectural and interior design services that 
                  blend functionality with aesthetic excellence.
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="text-center p-6 h-full">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Award className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Excellence</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Committed to the highest standards of design quality, project delivery, 
                  and client satisfaction in every project we undertake.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </motion.section>

      {/* Services Overview */}
      <motion.section variants={itemVariants}>
        <div className="text-center mb-12">
          <h2 className="font-heading text-3xl mb-4">What We Do</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            From concept to completion, we provide comprehensive architectural and design services.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            "Architectural Design",
            "Interior Design", 
            "BIM Services",
            "Execution Drawings",
            "Facade Design",
            "Landscape Design",
            "Project Management",
            "3D Visualization"
          ].map((service, index) => (
            <motion.div
              key={service}
              variants={itemVariants}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-4 text-center hover:shadow-lg transition-shadow">
                <CardContent className="p-2">
                  <h3 className="font-semibold">{service}</h3>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>
    </motion.div>
  );
}
