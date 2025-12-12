import { Link } from 'react-router-dom';
import {
    Sparkles, Wand2, Zap, Shield, Palette, ArrowRight,
    Check, Star, Users, TrendingUp, Globe, Clock
} from 'lucide-react';

const Landing = () => {
    const features = [
        {
            icon: Sparkles,
            title: 'AI Image Enhancement',
            description: 'Transform blurry, low-quality images into crystal-clear masterpieces',
            gradient: 'from-purple-500 to-pink-500',
        },
        {
            icon: Wand2,
            title: 'Text-to-Image Generation',
            description: 'Create stunning visuals from simple text descriptions',
            gradient: 'from-blue-500 to-cyan-500',
        },
        {
            icon: Palette,
            title: 'Style Transfer',
            description: 'Apply artistic styles and transform your images instantly',
            gradient: 'from-green-500 to-emerald-500',
        },
    ];

    const benefits = [
        {
            icon: Zap,
            title: 'Lightning Fast',
            description: 'Process images in seconds with our optimized AI models',
        },
        {
            icon: Shield,
            title: 'Secure & Private',
            description: 'Your data is encrypted and never shared with third parties',
        },
        {
            icon: Globe,
            title: 'Cloud-Based',
            description: 'Access from anywhere, anytime on any device',
        },
        {
            icon: Clock,
            title: '24/7 Availability',
            description: 'Always online and ready to process your images',
        },
    ];

    const pricingPlans = [
        {
            name: 'Free',
            price: '$0',
            period: '/month',
            description: 'Perfect for trying out our platform',
            features: [
                '10 image enhancements/month',
                '5 text-to-image generations/month',
                'Standard processing speed',
                'Basic support',
            ],
            cta: 'Get Started',
            popular: false,
        },
        {
            name: 'Pro',
            price: '$19',
            period: '/month',
            description: 'For professionals and creators',
            features: [
                'Unlimited enhancements',
                '100 generations/month',
                'Priority processing',
                'Advanced features',
                'Email support',
                'HD quality exports',
            ],
            cta: 'Start Free Trial',
            popular: true,
        },
        {
            name: 'Enterprise',
            price: 'Custom',
            period: '',
            description: 'For teams and organizations',
            features: [
                'Everything in Pro',
                'Unlimited generations',
                'API access',
                'Custom models',
                'Dedicated support',
                'SLA guarantee',
            ],
            cta: 'Contact Sales',
            popular: false,
        },
    ];

    const testimonials = [
        {
            name: 'Sarah Johnson',
            role: 'Product Designer',
            avatar: 'https://i.pravatar.cc/150?img=1',
            content: 'Deep Vision has revolutionized my workflow. The AI enhancement is simply incredible!',
            rating: 5,
        },
        {
            name: 'Michael Chen',
            role: 'Content Creator',
            avatar: 'https://i.pravatar.cc/150?img=2',
            content: 'The text-to-image generation is mind-blowing. It saves me hours of work every day.',
            rating: 5,
        },
        {
            name: 'Emily Rodriguez',
            role: 'Marketing Manager',
            avatar: 'https://i.pravatar.cc/150?img=3',
            content: 'Professional results in seconds. This tool is a game-changer for our marketing team.',
            rating: 5,
        },
    ];

    const stats = [
        { value: '100K+', label: 'Images Processed' },
        { value: '10K+', label: 'Happy Users' },
        { value: '99.9%', label: 'Uptime' },
        { value: '4.9/5', label: 'User Rating' },
    ];

    return (
        <div className="min-h-screen bg-white dark:bg-gray-950">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800">
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg">
                                <span className="text-white font-bold text-xl">DV</span>
                            </div>
                            <span className="font-bold text-xl bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                                Deep Vision
                            </span>
                        </div>

                        <div className="hidden md:flex items-center gap-8">
                            <a href="#features" className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                                Features
                            </a>
                            <a href="#pricing" className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                                Pricing
                            </a>
                            <a href="#testimonials" className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                                Testimonials
                            </a>
                        </div>

                        <div className="flex items-center gap-4">
                            <Link
                                to="/login"
                                className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors font-medium"
                            >
                                Login
                            </Link>
                            <Link
                                to="/register"
                                className="px-6 py-2 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-105"
                            >
                                Sign Up Free
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-4">
                <div className="container mx-auto max-w-6xl text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary-500/10 to-accent-500/10 border border-primary-500/20 text-primary-700 dark:text-primary-300 text-sm font-medium mb-6 animate-fade-in">
                        <Star className="w-4 h-4 fill-current" />
                        <span>Trusted by 10,000+ users worldwide</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary-600 via-accent-600 to-primary-600 bg-clip-text text-transparent leading-tight animate-fade-in">
                        Transform Images with
                        <br />
                        AI-Powered Magic
                    </h1>

                    <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-10 max-w-3xl mx-auto animate-fade-in">
                        Professional-grade image enhancement and generation powered by cutting-edge AI.
                        Create stunning visuals in seconds.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in">
                        <Link
                            to="/register"
                            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold shadow-lg shadow-primary-500/50 hover:shadow-xl hover:shadow-primary-500/60 transition-all duration-300 hover:scale-105"
                        >
                            <span>Start Free Trial</span>
                            <ArrowRight className="w-5 h-5" />
                        </Link>

                        <Link
                            to="/login"
                            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-all duration-300"
                        >
                            <span>View Demo</span>
                        </Link>
                    </div>

                    {/* Hero Image/Demo */}
                    <div className="mt-16 relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-accent-500/20 blur-3xl"></div>
                        <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-gray-200 dark:border-gray-800">
                            <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center">
                                <div className="text-center">
                                    <Sparkles className="w-20 h-20 text-primary-500 mx-auto mb-4 animate-pulse" />
                                    <p className="text-gray-600 dark:text-gray-400">Platform Demo</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-16 bg-gray-50 dark:bg-gray-900">
                <div className="container mx-auto px-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
                        {stats.map((stat, index) => (
                            <div key={index} className="text-center">
                                <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent mb-2">
                                    {stat.value}
                                </div>
                                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-20 px-4">
                <div className="container mx-auto max-w-6xl">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                            Powerful AI Features
                        </h2>
                        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                            Everything you need to create and enhance stunning images
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {features.map((feature, index) => {
                            const Icon = feature.icon;
                            return (
                                <div
                                    key={index}
                                    className="group p-8 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-transparent hover:shadow-2xl hover:shadow-primary-500/20 transition-all duration-300 hover:-translate-y-2"
                                >
                                    <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                                        <Icon className="w-8 h-8 text-white" />
                                    </div>

                                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                                        {feature.title}
                                    </h3>

                                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section className="py-20 px-4 bg-gray-50 dark:bg-gray-900">
                <div className="container mx-auto max-w-6xl">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                            Why Choose Deep Vision?
                        </h2>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {benefits.map((benefit, index) => {
                            const Icon = benefit.icon;
                            return (
                                <div
                                    key={index}
                                    className="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                                >
                                    <Icon className="w-12 h-12 text-primary-500 mb-4" />
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                                        {benefit.title}
                                    </h3>
                                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                                        {benefit.description}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-20 px-4">
                <div className="container mx-auto max-w-6xl">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                            Simple, Transparent Pricing
                        </h2>
                        <p className="text-xl text-gray-600 dark:text-gray-400">
                            Choose the perfect plan for your needs
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {pricingPlans.map((plan, index) => (
                            <div
                                key={index}
                                className={`relative p-8 rounded-2xl border-2 transition-all duration-300 hover:-translate-y-2 ${plan.popular
                                        ? 'border-primary-500 bg-gradient-to-b from-primary-50 to-white dark:from-primary-900/20 dark:to-gray-800 shadow-xl'
                                        : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary-500'
                                    }`}
                            >
                                {plan.popular && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-primary-500 to-accent-500 text-white text-sm font-semibold">
                                        Most Popular
                                    </div>
                                )}

                                <div className="text-center mb-6">
                                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                                        {plan.name}
                                    </h3>
                                    <div className="flex items-baseline justify-center gap-1 mb-2">
                                        <span className="text-5xl font-bold text-gray-900 dark:text-white">
                                            {plan.price}
                                        </span>
                                        <span className="text-gray-600 dark:text-gray-400">
                                            {plan.period}
                                        </span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                                        {plan.description}
                                    </p>
                                </div>

                                <ul className="space-y-4 mb-8">
                                    {plan.features.map((feature, idx) => (
                                        <li key={idx} className="flex items-start gap-3">
                                            <Check className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                                            <span className="text-gray-700 dark:text-gray-300">
                                                {feature}
                                            </span>
                                        </li>
                                    ))}
                                </ul>

                                <Link
                                    to="/register"
                                    className={`block w-full py-3 rounded-xl font-semibold text-center transition-all ${plan.popular
                                            ? 'bg-gradient-to-r from-primary-500 to-accent-500 text-white shadow-lg hover:shadow-xl hover:scale-105'
                                            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                                        }`}
                                >
                                    {plan.cta}
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonials Section */}
            <section id="testimonials" className="py-20 px-4 bg-gray-50 dark:bg-gray-900">
                <div className="container mx-auto max-w-6xl">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                            Loved by Creators Worldwide
                        </h2>
                        <p className="text-xl text-gray-600 dark:text-gray-400">
                            See what our users have to say
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {testimonials.map((testimonial, index) => (
                            <div
                                key={index}
                                className="p-6 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                            >
                                <div className="flex gap-1 mb-4">
                                    {[...Array(testimonial.rating)].map((_, i) => (
                                        <Star
                                            key={i}
                                            className="w-5 h-5 fill-yellow-400 text-yellow-400"
                                        />
                                    ))}
                                </div>

                                <p className="text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                                    "{testimonial.content}"
                                </p>

                                <div className="flex items-center gap-3">
                                    <img
                                        src={testimonial.avatar}
                                        alt={testimonial.name}
                                        className="w-12 h-12 rounded-full"
                                    />
                                    <div>
                                        <div className="font-semibold text-gray-900 dark:text-white">
                                            {testimonial.name}
                                        </div>
                                        <div className="text-sm text-gray-600 dark:text-gray-400">
                                            {testimonial.role}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-4">
                <div className="container mx-auto max-w-4xl">
                    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary-500 via-accent-500 to-primary-500 p-12 text-center text-white">
                        <div className="absolute inset-0 bg-black/10"></div>
                        <div className="relative z-10">
                            <h2 className="text-4xl md:text-5xl font-bold mb-6">
                                Ready to Transform Your Images?
                            </h2>
                            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
                                Join thousands of creators and start creating stunning visuals with AI today
                            </p>
                            <Link
                                to="/register"
                                className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-primary-600 font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105"
                            >
                                <span>Start Free Trial</span>
                                <ArrowRight className="w-5 h-5" />
                            </Link>
                            <p className="mt-4 text-white/80 text-sm">
                                No credit card required • Cancel anytime
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-4 bg-gray-900 text-gray-400">
                <div className="container mx-auto max-w-6xl">
                    <div className="grid md:grid-cols-4 gap-8 mb-8">
                        <div>
                            <div className="flex items-center gap-2 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                    <span className="text-white font-bold">DV</span>
                                </div>
                                <span className="font-bold text-white">Deep Vision</span>
                            </div>
                            <p className="text-sm">
                                AI-powered image enhancement and generation platform
                            </p>
                        </div>

                        <div>
                            <h3 className="font-semibold text-white mb-4">Product</h3>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                            </ul>
                        </div>

                        <div>
                            <h3 className="font-semibold text-white mb-4">Company</h3>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                            </ul>
                        </div>

                        <div>
                            <h3 className="font-semibold text-white mb-4">Legal</h3>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
                            </ul>
                        </div>
                    </div>

                    <div className="pt-8 border-t border-gray-800 text-center text-sm">
                        <p>© 2025 Deep Vision. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
