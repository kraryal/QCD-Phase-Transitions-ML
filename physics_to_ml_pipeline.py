"""
Physics to ML Pipeline: Converting Computational Results to Data Science
=======================================================================
Demonstrates how Fortran computational physics results can be transformed
into machine learning training data and business applications.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns

plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)

class PhysicsToMLPipeline:
    """Convert computational physics results to ML-ready datasets"""
    
    def __init__(self):
        self.physics_data = None
        self.ml_model = None
        
    def simulate_fortran_output(self, n_samples=2000):
        """
        Simulate typical output from Fortran CMF model calculations
        In practice, this would load actual Fortran output files
        """
        print("🔬 STEP 1: Loading Computational Physics Data")
        print("=" * 45)
        print("Source: Chiral Mean Field (CMF) model calculations")
        print("Language: Fortran (high-performance numerical computing)")
        print()
        
        np.random.seed(42)
        
        # Simulate physics parameters from your CMF model
        # Based on typical ranges from QCD phase transition studies
        data = {
            'temperature_MeV': np.random.uniform(50, 200, n_samples),
            'baryon_chemical_potential': np.random.uniform(0, 1200, n_samples),
            'charge_chemical_potential': np.random.uniform(-150, 100, n_samples),
            'strangeness_chemical_potential': np.random.uniform(-100, 50, n_samples),
            'charge_fraction_YQ': np.random.uniform(-0.5, 0.5, n_samples),
            'baryon_density': np.random.uniform(0, 8, n_samples),  # in nuclear density units
            'energy_density': np.random.uniform(0, 15, n_samples),  # GeV/fm³
            'pressure': np.random.uniform(0, 5, n_samples),  # GeV/fm³
        }
        
        df = pd.DataFrame(data)
        
        # Create physics-informed phase labels
        # This represents the phase boundary from your CMF calculations
        phase_condition = (
            (df['temperature_MeV'] > 150) |  # High temperature deconfinement
            (df['baryon_chemical_potential'] > 800) |  # High density deconfinement
            ((df['baryon_density'] > 4) & (df['temperature_MeV'] > 100))
        )
        
        df['phase'] = phase_condition.astype(int)  # 0=hadronic, 1=quark
        df['deconfinement_parameter'] = np.where(phase_condition, 
                                                np.random.uniform(0.7, 1.0, n_samples),
                                                np.random.uniform(0.0, 0.3, n_samples))
        
        self.physics_data = df
        
        print(f"✅ Loaded {len(df)} computational data points")
        print(f"✅ Features: {len(df.columns)-2} thermodynamic parameters")
        print(f"✅ Phase distribution: {(df['phase']==0).sum()} hadronic, {(df['phase']==1).sum()} quark")
        print()
        
        return df
    
    def feature_engineering(self):
        """Create physics-informed features for ML"""
        print("🛠️ STEP 2: Physics-Informed Feature Engineering")
        print("=" * 45)
        
        df = self.physics_data.copy()
        
        # Create derived features based on physics knowledge
        df['mu_B_over_T'] = df['baryon_chemical_potential'] / (df['temperature_MeV'] + 1e-6)
        df['energy_over_pressure'] = df['energy_density'] / (df['pressure'] + 1e-6)
        df['charge_asymmetry'] = np.abs(df['charge_fraction_YQ'])
        df['thermal_parameter'] = df['temperature_MeV'] / 200  # Normalized temperature
        df['density_parameter'] = df['baryon_density'] / 1.0  # Nuclear density units
        
        # Interaction terms (physics-motivated)
        df['T_mu_interaction'] = df['temperature_MeV'] * df['baryon_chemical_potential'] / 1000
        df['charge_density_coupling'] = df['charge_fraction_YQ'] * df['baryon_density']
        
        print("✅ Created physics-derived features:")
        print("   • μB/T ratio (deconfinement indicator)")
        print("   • Energy/Pressure ratio (equation of state)")
        print("   • Charge asymmetry (isospin effects)")
        print("   • Normalized thermal parameters")
        print("   • Interaction terms")
        print()
        
        # Select features for ML
        feature_columns = [
            'temperature_MeV', 'baryon_chemical_potential', 'charge_chemical_potential',
            'charge_fraction_YQ', 'baryon_density', 'energy_density',
            'mu_B_over_T', 'energy_over_pressure', 'charge_asymmetry',
            'thermal_parameter', 'T_mu_interaction'
        ]
        
        self.physics_data = df
        self.feature_columns = feature_columns
        
        return df[feature_columns], df['phase']
    
    def train_ml_models(self, X, y):
        """Train ML models on physics data"""
        print("🤖 STEP 3: Machine Learning Model Training")
        print("=" * 40)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Train Random Forest (good for physics data with non-linear relationships)
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        
        rf_model.fit(X_train, y_train)
        self.ml_model = rf_model
        
        # Evaluate model
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
        
        print(f"✅ Model Performance:")
        print(f"   • Test Accuracy: {accuracy:.1%}")
        print(f"   • CV Mean: {cv_scores.mean():.1%} (±{cv_scores.std()*2:.1%})")
        print(f"   • Training samples: {len(X_train)}")
        print(f"   • Test samples: {len(X_test)}")
        print()
        
        # Feature importance analysis
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("📊 Feature Importance (Physics Interpretation):")
        for _, row in feature_importance.head(5).iterrows():
            print(f"   • {row['feature']}: {row['importance']:.3f}")
        print()
        
        return rf_model, accuracy, feature_importance
    
    def create_visualizations(self, X, y, feature_importance):
        """Create professional visualizations"""
        print("📈 STEP 4: Data Visualization & Analysis")
        print("=" * 35)
        
        # 1. Phase distribution in parameter space
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('QCD Phase Transitions: Computational Physics → ML Analysis', fontsize=16, fontweight='bold')
        
        # Temperature vs Chemical Potential
        scatter = axes[0,0].scatter(X['temperature_MeV'], X['baryon_chemical_potential'], 
                                  c=y, cmap='RdYlBu', alpha=0.6)
        axes[0,0].set_xlabel('Temperature (MeV)')
        axes[0,0].set_ylabel('Baryon Chemical Potential (MeV)')
        axes[0,0].set_title('Phase Diagram: T vs μB')
        plt.colorbar(scatter, ax=axes[0,0], label='Phase (0=Hadronic, 1=Quark)')
        
        # Density vs Energy
        scatter2 = axes[0,1].scatter(X['baryon_density'], X['energy_density'], 
                                   c=y, cmap='RdYlBu', alpha=0.6)
        axes[0,1].set_xlabel('Baryon Density (n₀)')
        axes[0,1].set_ylabel('Energy Density (GeV/fm³)')
        axes[0,1].set_title('Equation of State: Density vs Energy')
        
        # Feature importance
        top_features = feature_importance.head(8)
        axes[1,0].barh(top_features['feature'], top_features['importance'])
        axes[1,0].set_xlabel('Importance')
        axes[1,0].set_title('ML Feature Importance')
        axes[1,0].tick_params(axis='y', labelsize=10)
        
        # Phase distribution
        phase_counts = pd.Series(y).value_counts()
        axes[1,1].pie(phase_counts.values, labels=['Hadronic', 'Quark'], 
                     autopct='%1.1f%%', colors=['lightblue', 'orange'])
        axes[1,1].set_title('Phase Distribution in Dataset')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Generated comprehensive analysis visualizations")
        print("✅ Shows phase boundaries, feature importance, and data distribution")
        print()
    
    def business_applications(self):
        """Demonstrate business applications"""
        print("💼 STEP 5: Business Applications & Career Relevance")
        print("=" * 50)
        
        applications = [
            {
                'domain': '🏭 Manufacturing',
                'physics': 'Phase transition detection',
                'business': 'Quality control and defect prediction',
                'skills': 'Anomaly detection, process monitoring'
            },
            {
                'domain': '💰 Finance', 
                'physics': 'Critical point analysis',
                'business': 'Market regime detection and risk assessment',
                'skills': 'Time series analysis, regime switching models'
            },
            {
                'domain': '🛒 E-commerce',
                'physics': 'Multi-parameter optimization',
                'business': 'Customer segmentation and recommendation systems',
                'skills': 'Clustering, collaborative filtering'
            },
            {
                'domain': '🏥 Healthcare',
                'physics': 'Thermodynamic equilibrium',
                'business': 'Biomarker analysis and diagnostic modeling',
                'skills': 'Classification, feature selection'
            },
            {
                'domain': '🚚 Supply Chain',
                'physics': 'Complex system dynamics',
                'business': 'Demand forecasting and inventory optimization',
                'skills': 'Forecasting, optimization algorithms'
            }
        ]
        
        for app in applications:
            print(f"{app['domain']}")
            print(f"   Physics: {app['physics']}")
            print(f"   Business: {app['business']}")
            print(f"   ML Skills: {app['skills']}")
            print()
        
        print("🎯 KEY TRANSFERABLE SKILLS:")
        print("   ✅ Complex data analysis and pattern recognition")
        print("   ✅ Multi-parameter optimization and feature engineering")
        print("   ✅ Model validation and performance assessment") 
        print("   ✅ High-performance computing and scalable algorithms")
        print("   ✅ Research methodology and reproducible analysis")
        print()

def main():
    """Run complete physics-to-ML pipeline demonstration"""
    print("🔬→🤖 COMPUTATIONAL PHYSICS TO DATA SCIENCE PIPELINE")
    print("=" * 60)
    print("Krishna Royal - Demonstrating research-to-industry skill transfer")
    print("Published Research: https://doi.org/10.1103/PhysRevD.102.076016")
    print()
    
    # Initialize pipeline
    pipeline = PhysicsToMLPipeline()
    
    # Step 1: Load computational physics data
    physics_df = pipeline.simulate_fortran_output(n_samples=2000)
    
    # Step 2: Feature engineering
    X, y = pipeline.feature_engineering()
    
    # Step 3: Train ML models
    model, accuracy, feature_importance = pipeline.train_ml_models(X, y)
    
    # Step 4: Create visualizations
    pipeline.create_visualizations(X, y, feature_importance)
    
    # Step 5: Business applications
    pipeline.business_applications()
    
    print("🚀 READY FOR DATA SCIENCE ROLES!")
    print("=" * 30)
    print("This pipeline demonstrates:")
    print("✅ Advanced computational background with published research")
    print("✅ Ability to transform domain expertise into ML solutions")
    print("✅ Complete data science workflow from raw data to insights")
    print("✅ Business acumen in translating technical skills")
    print("✅ Professional-grade code and visualization capabilities")

if __name__ == "__main__":
    main()