import './ThemesTags.css';

export function ThemesTags({ themes }) {
  return (
    <div className="themes-container">
      <div className="themes-header">
        <h2 className="section-title">Key Themes</h2>
      </div>
      <div className="themes-tags-wrapper">
        {themes.map((theme, index) => (
          <span key={index} className="theme-tag">
            #{theme}
          </span>
        ))}
      </div>
    </div>
  );
}
