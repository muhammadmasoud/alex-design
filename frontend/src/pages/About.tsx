import { motion } from "framer-motion";
import { ExternalLink, Award, Users, Target, Eye, ChevronLeft, ChevronRight, MapPin, Building, Layers, Palette, Hammer, Laptop, UserCheck, TrendingUp } from "lucide-react";
import { useState } from "react";
import SEO from "@/components/SEO";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { containerVariants, itemVariants } from "@/components/PageTransition";

interface TeamMember {
  id: string;
  name: string;
  title: string;
  description: string;
  qualifications: string[];
  experience: string[];
  imageUrl?: string;
  fallbackInitials: string;
}

const teamMembers: TeamMember[] = [
  {
    id: "muhammad",
    name: "Muhammad Ali Aboelhamd Ali Mahmoud",
    title: "Founder & Team Leader",
    description: "Muhammad Ali leads Alexandria Design with international experience spanning Europe, Turkey, and the Gulf region. As a member of the RIAI (Ireland) and the Egyptian Engineering Syndicate, he combines technical expertise with design innovation.",
    qualifications: [
      "Master in Architecture",
      "BIM Coordinator", 
      "Technical Architect",
      "Team Leader"
    ],
    experience: [
      "Specialized in BIM Coordination, execution drawings, and sustainable architecture",
      "Worked with Foster + Partners, Hellinikon S.M.S.A., maceJacobs, and BBI-INTRAKAT on the Riviera Towers (Greece)",
      "Academic background: M.Arch (Altınbaş University, Turkey) and B.Arch (Alexandria University)"
    ],
    imageUrl: "../assets/team/aboelhamd.jpeg",
    fallbackInitials: "MA"
  },
  {
    id: "islam",
    name: "Islam Marghany",
    title: "Interior Design Leader",
    description: "Islam brings extensive experience in design coordination, 3D modeling, and project management. With a strong academic background from Alexandria University (BSc in Architectural Engineering, Very Good with Honors), he has led projects at Emad Nathan Architecture and contributed to large-scale consultancy work.",
    qualifications: [
      "Senior Architect",
      "Specialist in Public Buildings & Interior Coordination",
      "BSc in Architectural Engineering (Very Good with Honors)"
    ],
    experience: [
      "Extensive experience in design coordination and 3D modeling",
      "Led projects at Emad Nathan Architecture",
      "Contributed to large-scale consultancy work",
      "Ensures interior design concepts are both innovative and practical"
    ],
    imageUrl: "../assets/team/eslam.jpeg",
    fallbackInitials: "IM"
  },
  {
    id: "abdullah",
    name: "Abdullah Ahmed",
    title: "Finishing & Site Works Leader",
    description: "Abdullah leads the finishing and on-site interior works, ensuring that design quality is faithfully executed in construction. His attention to detail guarantees flawless finishes and site coordination.",
    qualifications: [
      "Site Works Specialist",
      "Finishing Expert",
      "Construction Coordination"
    ],
    experience: [
      "Leads finishing and on-site interior works",
      "Ensures design quality is faithfully executed in construction",
      "Attention to detail guarantees flawless finishes",
      "Expert in site coordination"
    ],
    imageUrl: "../assets/team/abdullah.jpeg",
    fallbackInitials: "AA"
  },
  {
    id: "aya",
    name: "Aya Mohsen",
    title: "Execution Drawings Leader",
    description: "Aya specializes in detailed execution drawings for interiors, bridging the gap between concept and construction. Her precision ensures projects are buildable, efficient, and aligned with client expectations.",
    qualifications: [
      "Execution Drawings Specialist",
      "Interior Design Technical Expert",
      "Construction Documentation"
    ],
    experience: [
      "Specializes in detailed execution drawings for interiors",
      "Bridges the gap between concept and construction",
      "Precision ensures projects are buildable and efficient",
      "Aligned with client expectations"
    ],
    imageUrl: "../assets/team/aya.jpg",
    fallbackInitials: "AM"
  },
  {
    id: "abdelrahman",
    name: "Abdelrahman Ibrahim",
    title: "Shop Drawings & Manufacturing Leader",
    description: "Abdelrahman heads shop drawings, manufacturing details, and MEP integration. His technical knowledge enables smooth workflows between design, fabrication, and on-site execution, especially for furniture production and green wall systems.",
    qualifications: [
      "Shop Drawings Specialist",
      "Manufacturing Details Expert",
      "MEP Integration Coordinator"
    ],
    experience: [
      "Heads shop drawings and manufacturing details",
      "Expert in MEP integration",
      "Enables smooth workflows between design, fabrication, and execution",
      "Specializes in furniture production and green wall systems"
    ],
    imageUrl: "../assets/team/ozil.jpeg",
    fallbackInitials: "AI"
  },
  {
    id: "mostafa",
    name: "Mostafa Mahmoud",
    title: "AutoCAD Drafting & Site Supervision",
    description: "Mostafa supports the team with technical drafting and site supervision, ensuring coordination between design documents and on-site realities.",
    qualifications: [
      "AutoCAD Specialist",
      "Technical Drafting Expert",
      "Site Supervision"
    ],
    experience: [
      "Supports the team with technical drafting",
      "Expert in site supervision",
      "Ensures coordination between design documents and on-site realities",
      "Technical documentation specialist"
    ],
    imageUrl: "../assets/team/mostafa.jpg",
    fallbackInitials: "MM"
  },
  {
    id: "ruan",
    name: "Ruan Mohamed",
    title: "Client Relations & Digital Management",
    description: "Ruan manages the website, social media, WhatsApp communications, and client timelines, keeping projects well-organized and clients constantly updated.",
    qualifications: [
      "Digital Management Specialist",
      "Client Relations Expert",
      "Communication Coordinator"
    ],
    experience: [
      "Manages website and social media",
      "Handles WhatsApp communications",
      "Manages client timelines",
      "Keeps projects well-organized and clients updated"
    ],
    imageUrl: "../assets/team/ruan.jpg",
    fallbackInitials: "RM"
  },
  {
    id: "freddie",
    name: "Freddie Y. Sassine",
    title: "Business Development & Marketing",
    description: "Freddie provides management services and marketing strategies, helping Alexandria Design grow its network and expand internationally.",
    qualifications: [
      "Business Development Expert",
      "Marketing Strategist",
      "International Expansion Specialist"
    ],
    experience: [
      "Provides management services and marketing strategies",
      "Helps Alexandria Design grow its network",
      "Focuses on international expansion",
      "Strategic business development"
    ],
    imageUrl: "../assets/team/freddie.jpg",
    fallbackInitials: "FS"
  }
];

export default function About() {
  const [currentMemberIndex, setCurrentMemberIndex] = useState(0);
  const currentMember = teamMembers[currentMemberIndex];

  const nextMember = () => {
    setCurrentMemberIndex((prev) => (prev + 1) % teamMembers.length);
  };

  const prevMember = () => {
    setCurrentMemberIndex((prev) => (prev - 1 + teamMembers.length) % teamMembers.length);
  };

  return (
    <motion.div
      className="container py-16 sm:py-20 px-4 sm:px-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <SEO 
        title="About Us – Alexandria Design" 
        description="Learn about Alexandria Design, our vision, our founder Muhammad Ali Aboelhamd, and our expert team of architects and designers." 
        canonical="/about" 
      />

      {/* Hero Section */}
      <motion.section className="text-center mb-16 sm:mb-20" variants={itemVariants}>
        <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl mb-6 sm:mb-8">About Us – Alexandria Design</h1>
        <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed px-4">
          Creating sustainable, functional, and inspiring environments that enhance lives through innovative architectural design.
        </p>
      </motion.section>

      {/* Our Vision */}
      <motion.section className="mb-16 sm:mb-20" variants={itemVariants}>
        <Card className="max-w-5xl mx-auto p-8 sm:p-12 bg-gradient-to-br from-primary/5 to-primary/10">
          <CardContent className="text-center">
            <h2 className="font-heading text-3xl sm:text-4xl mb-6 text-primary">Our Vision</h2>
            <p className="text-lg sm:text-xl text-muted-foreground leading-relaxed max-w-4xl mx-auto">
              At Alexandria Design, we believe architecture is more than just buildings—it's about creating sustainable, functional, and inspiring environments that enhance lives. From design concepts to execution, we integrate creativity with precision, ensuring every project reflects innovation, sustainability, and client needs.
            </p>
          </CardContent>
        </Card>
      </motion.section>

      {/* Founder & Team Leader */}
      <motion.section className="mb-16 sm:mb-20" variants={itemVariants}>
        <Card className="max-w-6xl mx-auto">
          <CardHeader className="text-center pb-6">
            <h2 className="font-heading text-3xl sm:text-4xl mb-4 text-primary">Founder & Team Leader</h2>
          </CardHeader>
          <CardContent className="p-8 sm:p-12">
            <div className="grid lg:grid-cols-2 gap-8 sm:gap-12 items-center">
              <div>
                <motion.div variants={itemVariants}>
                  <h3 className="font-heading text-2xl sm:text-3xl mb-4 font-bold">Muhammad Ali Aboelhamd Ali Mahmoud</h3>
                  <Badge variant="outline" className="mb-4 text-sm px-3 py-1">Master in Architecture | BIM Coordinator | Technical Architect | Team Leader</Badge>
                  <p className="text-base sm:text-lg text-muted-foreground mb-6 leading-relaxed">
                    Muhammad Ali leads Alexandria Design with international experience spanning Europe, Turkey, and the Gulf region. As a member of the RIAI (Ireland) and the Egyptian Engineering Syndicate, he combines technical expertise with design innovation.
                  </p>
                  
                  <div className="space-y-4 mb-6">
                    <div className="flex items-start gap-3">
                      <Award className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                      <span className="text-sm sm:text-base">Specialized in BIM Coordination, execution drawings, and sustainable architecture.</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <Building className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                      <span className="text-sm sm:text-base">Worked with Foster + Partners, Hellinikon S.M.S.A., maceJacobs, and BBI-INTRAKAT on the Riviera Towers (Greece).</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <Target className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                      <span className="text-sm sm:text-base">Academic background: M.Arch (Altınbaş University, Turkey) and B.Arch (Alexandria University)</span>
                    </div>
                  </div>

                  <Button asChild size="lg" className="w-full sm:w-auto">
                    <a 
                      href="https://www.behance.net/mohamedaboelhamd" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-2"
                    >
                      View Portfolio on Behance
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                </motion.div>
              </div>

              <motion.div variants={itemVariants} className="mt-8 lg:mt-0">
                <Card className="p-6 sm:p-8 bg-gradient-to-br from-primary/5 to-primary/10">
                  <CardContent className="p-0">
                    <div className="grid grid-cols-2 gap-6 text-center">
                      <div>
                        <div className="text-3xl sm:text-4xl font-bold text-primary mb-2">86K+</div>
                        <div className="text-sm text-muted-foreground">Project Views</div>
                      </div>
                      <div>
                        <div className="text-3xl sm:text-4xl font-bold text-primary mb-2">14K+</div>
                        <div className="text-sm text-muted-foreground">Appreciations</div>
                      </div>
                      <div>
                        <div className="text-3xl sm:text-4xl font-bold text-primary mb-2">4.7K+</div>
                        <div className="text-sm text-muted-foreground">Followers</div>
                      </div>
                      <div>
                        <div className="text-3xl sm:text-4xl font-bold text-primary mb-2">10+</div>
                        <div className="text-sm text-muted-foreground">Years Experience</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </CardContent>
        </Card>
      </motion.section>

      {/* Our Team - ENLARGED AND PROMINENT */}
      <motion.section className="mb-16 sm:mb-20 bg-gradient-to-b from-background to-primary/5 py-12 sm:py-16 -mx-4 sm:-mx-6 px-4 sm:px-6" variants={itemVariants}>
        <div className="container mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="font-heading text-4xl sm:text-5xl md:text-6xl mb-6 text-primary">Our Team</h2>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto px-4 leading-relaxed">
              Meet the talented professionals who bring our architectural visions to life. Each team member contributes unique expertise to ensure exceptional project delivery.
            </p>
          </div>

          <Card className="max-w-6xl mx-auto shadow-2xl border-2 border-primary/20">
            <CardContent className="p-8 sm:p-12">
              <div className="grid lg:grid-cols-2 gap-8 sm:gap-12 items-center justify-center min-h-[600px]">
                {/* Team Member Avatar - LARGER */}
                <motion.div 
                  className="text-center lg:text-left h-full flex flex-col justify-center"
                  key={currentMember.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="flex justify-center lg:justify-start mb-6">
                    <div className="relative">
                      <Avatar className="w-48 h-48 sm:w-56 sm:h-56 lg:w-64 lg:h-64 border-4 border-primary/20 shadow-xl">
                        {currentMember.imageUrl && (
                          <AvatarImage 
                            src={currentMember.imageUrl} 
                            alt={currentMember.name}
                            className="object-cover"
                          />
                        )}
                        <AvatarFallback className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-br from-primary/20 to-primary/30">
                          {currentMember.fallbackInitials}
                        </AvatarFallback>
                      </Avatar>
                    </div>
                  </div>
                  
                  <Badge variant="outline" className="mb-4 text-base px-4 py-2 border-primary/30 mx-auto lg:mx-0 w-fit">
                    {currentMember.title}
                  </Badge>
                  <h3 className="font-heading text-2xl sm:text-3xl font-bold mb-4 text-primary">
                    {currentMember.name}
                  </h3>
                </motion.div>

                {/* Team Member Details - ENHANCED WITH FIXED HEIGHT */}
                <motion.div
                  key={`${currentMember.id}-details`}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className="h-full flex flex-col justify-center min-h-[500px]"
                >
                  <div className="space-y-6">
                    <p className="text-base sm:text-lg text-muted-foreground leading-relaxed">
                      {currentMember.description}
                    </p>

                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold text-lg mb-3 text-primary flex items-center gap-2">
                          <Award className="h-5 w-5" />
                          Qualifications:
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {currentMember.qualifications.map((qual, index) => (
                            <Badge key={index} variant="secondary" className="text-sm px-3 py-1">
                              {qual}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-bold text-lg mb-3 text-primary flex items-center gap-2">
                          <Users className="h-5 w-5" />
                          Experience:
                        </h4>
                        <ul className="space-y-2">
                          {currentMember.experience.map((exp, index) => (
                            <li key={index} className="text-sm sm:text-base text-muted-foreground flex items-start gap-3">
                              <span className="text-primary mt-1.5 text-lg">•</span>
                              <span>{exp}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* Enhanced Navigation Controls */}
              <div className="flex items-center justify-between mt-8 pt-8 border-t-2 border-primary/20">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={prevMember}
                  disabled={teamMembers.length <= 1}
                  className="border-primary/30 hover:bg-primary/10"
                >
                  <ChevronLeft className="h-5 w-5 mr-2" />
                  Previous
                </Button>

                <div className="flex items-center gap-4">
                  <span className="text-base text-muted-foreground font-medium">
                    {currentMemberIndex + 1} of {teamMembers.length}
                  </span>
                  <div className="flex gap-2">
                    {teamMembers.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentMemberIndex(index)}
                        className={`w-3 h-3 rounded-full transition-all duration-200 ${
                          index === currentMemberIndex 
                            ? 'bg-primary scale-125' 
                            : 'bg-muted-foreground/30 hover:bg-muted-foreground/50 hover:scale-110'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="lg"
                  onClick={nextMember}
                  disabled={teamMembers.length <= 1}
                  className="border-primary/30 hover:bg-primary/10"
                >
                  Next
                  <ChevronRight className="h-5 w-5 ml-2" />
                </Button>
              </div>

              {/* Team Overview Stats */}
              <div className="mt-8 pt-8 border-t border-primary/20">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-primary">{teamMembers.length}</div>
                    <div className="text-sm text-muted-foreground">Team Members</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary">50+</div>
                    <div className="text-sm text-muted-foreground">Projects Completed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary">10+</div>
                    <div className="text-sm text-muted-foreground">Years Combined Experience</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary">100%</div>
                    <div className="text-sm text-muted-foreground">Client Satisfaction</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.section>

      {/* What We Do */}
      <motion.section className="mb-16 sm:mb-20" variants={itemVariants}>
        <Card className="max-w-6xl mx-auto">
          <CardHeader className="text-center pb-8">
            <h2 className="font-heading text-3xl sm:text-4xl mb-4 text-primary">What We Do</h2>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto px-4">
              From concept to completion, we provide comprehensive architectural and design services that transform visions into reality.
            </p>
          </CardHeader>
          <CardContent className="p-8 sm:p-12">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: Building,
                  title: "Architectural Design",
                  description: "Concept to execution for residential, commercial, and public buildings."
                },
                {
                  icon: Palette,
                  title: "Interior Design & Finishing", 
                  description: "Innovative interior solutions with attention to detail."
                },
                {
                  icon: Layers,
                  title: "Execution & Shop Drawings",
                  description: "Precise documentation for seamless construction."
                },
                {
                  icon: UserCheck,
                  title: "Site Supervision",
                  description: "On-site quality control and project management."
                },
                {
                  icon: Hammer,
                  title: "Furniture Manufacturing",
                  description: "Custom-made furniture aligned with design concepts."
                },
                {
                  icon: Eye,
                  title: "Green Architecture",
                  description: "Specialized in green walls, terraces, and planter systems for sustainable living."
                }
              ].map((service, index) => (
                <motion.div
                  key={service.title}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-6 text-center hover:shadow-lg transition-all duration-300 h-full hover:scale-105 border-primary/20">
                    <CardHeader>
                      <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary/10 to-primary/20 rounded-xl flex items-center justify-center mb-4">
                        <service.icon className="h-8 w-8 text-primary" />
                      </div>
                      <CardTitle className="text-xl text-primary">{service.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground leading-relaxed">
                        {service.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.section>
    </motion.div>
  );
}
