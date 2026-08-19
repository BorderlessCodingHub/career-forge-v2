import { Zap, Globe, MessageCircle, Users, PlayCircle } from 'lucide-react';

const footerLinks = {
  Product: ['Features', 'Curriculum', 'Pricing', 'Testimonials', 'FAQ'],
  Resources: ['Blog', 'Documentation', 'Community', 'Podcast', 'Newsletter'],
  Company: ['About Us', 'Careers', 'Press Kit', 'Partners', 'Contact'],
  Legal: ['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'Refund Policy'],
};

const socialLinks = [
  { icon: MessageCircle, href: '#', label: 'Twitter' },
  { icon: Users, href: '#', label: 'LinkedIn' },
  { icon: Globe, href: '#', label: 'GitHub' },
  { icon: PlayCircle, href: '#', label: 'YouTube' },
];

export default function Footer() {
  return (
    <footer className="relative border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main footer */}
        <div className="py-12 md:py-16 grid grid-cols-2 md:grid-cols-6 gap-8">
          {/* Brand */}
          <div className="col-span-2">
            <a href="#" className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">
                Career<span className="gradient-text">Forge</span>
              </span>
            </a>
            <p className="text-sm text-surface-200/50 max-w-xs leading-relaxed mb-6">
              The premier career accelerator for software engineers transitioning into AI/LLM engineering. Built by engineers, for engineers.
            </p>

            {/* Social links */}
            <div className="flex gap-3">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  aria-label={social.label}
                  className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center text-surface-200/40 hover:text-white hover:bg-white/10 transition-all duration-300"
                >
                  <social.icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-sm font-semibold text-white mb-4">{title}</h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-surface-200/40 hover:text-white transition-colors duration-200"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="py-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-surface-200/30">
            © 2025 Career Forge. All rights reserved.
          </p>
          <p className="text-xs text-surface-200/30">
            Made with 🔥 for engineers who build the future
          </p>
        </div>
      </div>
    </footer>
  );
}
