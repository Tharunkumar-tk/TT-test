import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Settings, 
  User, 
  Target, 
  Trophy, 
  Calendar,
  Zap,
  Star
} from 'lucide-react';

// Import challenge images
import fullBodyImage from '@/assets/challenges/full-body.jpg';
import calisthenicsImage from '@/assets/challenges/calisthenics.jpg';
import flexibilityImage from '@/assets/challenges/flexibility.jpg';
import lowerBodyImage from '@/assets/challenges/lower-body.jpg';
import paraAthleteImage from '@/assets/challenges/para-athlete.jpg';

// Import activity images
import assistedChinDipImage from '@/assets/activities/assisted-chin-dip.jpg';
import modifiedShuttleRunImage from '@/assets/activities/modified-shuttle-run.jpg';
import assistedShuttleRunImage from '@/assets/activities/assisted-shuttle-run.jpg';
import enduranceRunImage from '@/assets/activities/800m-endurance-run.jpg';
import shuttleRunImage from '@/assets/activities/4x10m-shuttle-run.jpg';
import standingStartImage from '@/assets/activities/30m-standing-start.jpg';
import medicineBallThrowImage from '@/assets/activities/medicine-ball-throw.jpg';
import standingBroadJumpImage from '@/assets/activities/standing-broad-jump.jpg';
import standingVerticalJumpImage from '@/assets/activities/standing-vertical-jump.jpg';
import wideArmPushupImage from '@/assets/activities/wide-arm-pushup.jpg';
import kneePushupImage from '@/assets/activities/knee-pushup.jpg';
import inclinedPushupImage from '@/assets/activities/inclined-pushup.jpg';
import jumpingJackImage from '@/assets/activities/jumping-jack.jpg';
import chestStretchImage from '@/assets/activities/chest-stretch.jpg';
import cobraStretchImage from '@/assets/activities/cobra-stretch.jpg';
import plankImage from '@/assets/activities/plank.jpg';
import sitUpsImage from '@/assets/activities/sit-ups.jpg';
import shuttleRunGeneralImage from '@/assets/activities/shuttle-run.jpg';
import verticalJumpImage from '@/assets/activities/vertical-jump.jpg';

interface HomeScreenProps {
  userRole: 'athlete' | 'coach' | 'admin';
  userName: string;
  onTabChange: (tab: string) => void;
  activeTab: string;
  onProfileOpen?: () => void;
  onSettingsOpen?: () => void;
  onChallengeRedirect?: (challengeId: number) => void;
}

const HomeScreen = ({ userRole, userName, onTabChange, activeTab, onProfileOpen, onSettingsOpen, onChallengeRedirect }: HomeScreenProps) => {
  const [searchFocus, setSearchFocus] = useState(false);
  const [selectedChallengeFilter, setSelectedChallengeFilter] = useState<string | null>(null);

  const getChallengeImage = (challengeId: number) => {
    switch (challengeId) {
      case 1: return fullBodyImage;
      case 2: return calisthenicsImage;
      case 3: return flexibilityImage;
      case 4: return lowerBodyImage;
      case 5: return paraAthleteImage;
      default: return fullBodyImage;
    }
  };

  const challenges = [
    {
      id: 1,
      title: 'Full Body Challenge',
      type: 'challenge-blue',
      difficulty: 'Intermediate',
      duration: '4 weeks',
      participants: 1234,
      category: 'Strength'
    },
    {
      id: 2,
      title: 'Calisthenics Plan',
      type: 'challenge-purple',
      difficulty: 'Advanced',
      duration: '6 weeks',
      participants: 856,
      category: 'Calisthenics'
    },
    {
      id: 3,
      title: 'Kegel Power Boost',
      type: 'challenge-gray',
      difficulty: 'Beginner',
      duration: '2 weeks',
      participants: 2341,
      category: 'Flexibility'
    },
    {
      id: 4,
      title: 'Lower Body Challenge',
      type: 'challenge-light-blue',
      difficulty: 'Intermediate',
      duration: '3 weeks',
      participants: 987,
      category: 'Endurance'
    },
    {
      id: 5,
      title: 'Para-Athlete Challenge',
      type: 'challenge-maroon',
      difficulty: 'All Levels',
      duration: '5 weeks',
      participants: 456,
      category: 'Para-Athlete'
    }
  ];

  const challengeTags = ['Strength', 'Endurance', 'Flexibility', 'Calisthenics', 'Para-Athlete'];

  const getFilteredChallenges = () => {
    if (!selectedChallengeFilter) return challenges;
    return challenges.filter(challenge => challenge.category === selectedChallengeFilter);
  };

  const activityTags = [
    'Flexibility', 'Endurance', 'Arm', 'Chest', 'Shoulder', 'Leg', 'Para-Athlete'
  ];

  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const toggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const allActivities = [
    // Arm exercises
    { name: 'Push-ups', rating: 4.8, icon: '💪', muscles: 'Chest, Arms', tags: ['Arm', 'Chest'] },
    { name: 'Pull-ups', rating: 4.9, icon: '🔥', muscles: 'Back, Arms', tags: ['Arm'] },
    { name: 'Inclined Push-up', rating: 4.5, image: inclinedPushupImage, muscles: 'Chest, Arms', tags: ['Arm', 'Chest'] },
    { name: 'Knee Push-up', rating: 4.3, image: kneePushupImage, muscles: 'Chest, Arms', tags: ['Arm', 'Chest', 'Para-Athlete'] },
    { name: 'Wide Arm Push-up', rating: 4.6, image: wideArmPushupImage, muscles: 'Chest, Arms', tags: ['Arm', 'Chest'] },
    { name: 'Assisted Chin & Dip', rating: 4.4, image: assistedChinDipImage, muscles: 'Arms', tags: ['Arm', 'Para-Athlete'] },
    
    // Leg exercises
    { name: 'Vertical Jump', rating: 4.6, image: verticalJumpImage, muscles: 'Legs', tags: ['Leg'] },
    { name: 'Standing Vertical Jump', rating: 4.7, image: standingVerticalJumpImage, muscles: 'Legs', tags: ['Leg'] },
    { name: 'Standing Broad Jump', rating: 4.8, image: standingBroadJumpImage, muscles: 'Legs', tags: ['Leg'] },
    { name: '30-Meter Standing Start', rating: 4.5, image: standingStartImage, muscles: 'Legs', tags: ['Leg'] },
    
    // Endurance exercises
    { name: 'Shuttle Run', rating: 4.8, image: shuttleRunGeneralImage, muscles: 'Full Body', tags: ['Endurance', 'Leg'] },
    { name: '4 × 10-Meter Shuttle Run', rating: 4.7, image: shuttleRunImage, muscles: 'Full Body', tags: ['Endurance', 'Leg'] },
    { name: '800-Meter Endurance Run', rating: 4.9, image: enduranceRunImage, muscles: 'Full Body', tags: ['Endurance'] },
    { name: 'Assisted Shuttle Run', rating: 4.3, image: assistedShuttleRunImage, muscles: 'Full Body', tags: ['Endurance', 'Para-Athlete'] },
    { name: 'Modified Shuttle Run', rating: 4.2, image: modifiedShuttleRunImage, muscles: 'Full Body', tags: ['Endurance', 'Para-Athlete'] },
    
    // Flexibility exercises
    { name: 'Cobra Stretch', rating: 4.5, image: cobraStretchImage, muscles: 'Back', tags: ['Flexibility'] },
    { name: 'Chest Stretch', rating: 4.4, image: chestStretchImage, muscles: 'Chest', tags: ['Flexibility'] },
    { name: 'Sit-ups', rating: 4.7, image: sitUpsImage, muscles: 'Core', tags: ['Flexibility'] },
    
    // Core/General exercises
    { name: 'Plank', rating: 4.9, image: plankImage, muscles: 'Core', tags: [] },
    { name: 'Jumping Jack', rating: 4.6, image: jumpingJackImage, muscles: 'Full Body', tags: [] },
    { name: 'Medicine Ball Throw', rating: 4.8, image: medicineBallThrowImage, muscles: 'Shoulders, Arms', tags: ['Shoulder'] }
  ];

  const getFilteredActivities = () => {
    if (selectedTags.length === 0) return allActivities;
    return allActivities.filter(activity => 
      selectedTags.some(tag => activity.tags.includes(tag))
    );
  };

  const activities = getFilteredActivities();

  return (
    <div className="min-h-screen bg-background">
      {/* Top Bar */}
      <div className="sticky top-0 z-50 bg-primary border-b border-primary-dark safe-top">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between max-w-md mx-auto">
            <div>
              <h1 className="text-lg font-semibold text-white">Welcome, {userName}</h1>
              <p className="text-sm text-white/80 capitalize">{userRole}</p>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="ghost" size="sm" className="tap-target text-white hover:bg-white/20" onClick={onSettingsOpen}>
                <Settings className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="sm" className="tap-target text-white hover:bg-white/20" onClick={onProfileOpen}>
                <User className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 pb-20 max-w-md mx-auto">
        {/* Search Bar */}
        <div className="mb-6 relative">
          <div className={`relative transition-all duration-300 ${
            searchFocus ? 'transform scale-105' : ''
          }`}>
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search workouts, challenges..."
              className="pl-10 h-12 rounded-xl"
              onFocus={() => setSearchFocus(true)}
              onBlur={() => setSearchFocus(false)}
            />
          </div>
          {searchFocus && (
            <Card className="absolute top-full mt-2 w-full z-10 animate-slide-up">
              <CardContent className="p-3">
                <p className="text-sm text-muted-foreground">Search recommendations will appear here</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Weekly Goal Progress */}
        <Card className="mb-6 animate-fade-in">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Weekly Progress</CardTitle>
              <Badge variant="secondary" className="bg-success/20 text-success">
                🔥 5 day streak
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between mb-3">
              {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => (
                <div
                  key={day}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    index < 5
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-muted-foreground'
                  }`}
                >
                  {day}
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">5/7 days this week</span>
              <span className="text-primary font-medium">71% complete</span>
            </div>
          </CardContent>
        </Card>

        {/* Challenges Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Challenges</h2>
          </div>
          
          {/* Challenge Filter Tags */}
          <div className="flex flex-wrap gap-2 mb-4">
            <Button
              variant={selectedChallengeFilter === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedChallengeFilter(null)}
              className="rounded-full h-8 text-xs"
            >
              All
            </Button>
            {challengeTags.map((tag) => (
              <Button
                key={tag}
                variant={selectedChallengeFilter === tag ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedChallengeFilter(tag)}
                className="rounded-full h-8 text-xs"
              >
                {tag}
              </Button>
            ))}
          </div>
          
          {/* Horizontal Scrollable Challenge Cards */}
          <div className="flex space-x-4 overflow-x-auto pb-3 scrollbar-hide">
            {getFilteredChallenges().map((challenge) => (
              <Card 
                key={challenge.id} 
                className={`flex-shrink-0 w-48 overflow-hidden cursor-pointer hover:scale-105 transition-transform relative`}
                onClick={() => onChallengeRedirect?.(challenge.id)}
              >
                <div 
                  className="h-24 bg-cover bg-center relative"
                  style={{
                    backgroundImage: `url(${getChallengeImage(challenge.id)})`
                  }}
                >
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />
                </div>
                <CardContent className={`p-3 ${challenge.type} text-white`}>
                  <h3 className="font-semibold text-sm text-white leading-tight mb-2">
                    {challenge.title}
                  </h3>
                  <p className="text-xs opacity-90 mb-2">{challenge.difficulty}</p>
                  <div className="flex items-center justify-between text-xs">
                    <span>{challenge.duration}</span>
                    <Badge variant="outline" className="text-xs bg-white/20 text-white border-white/30">
                      {challenge.participants}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Activity Focus */}
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4">Activity Focus</h2>
          
          {/* Tags */}
           <div className="flex flex-wrap gap-2 mb-4">
            {activityTags.map((tag) => (
              <Button
                key={tag}
                variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  setSelectedTags(prev => 
                    prev.includes(tag) 
                      ? [] // Deselect if already selected
                      : [tag] // Select only this tag, deselect others
                  );
                }}
                className="rounded-full h-8 text-xs"
              >
                {tag}
              </Button>
            ))}
          </div>

          {/* Activities - Horizontal Scrollable */}
          <div className="flex space-x-4 overflow-x-auto pb-3 scrollbar-hide">
            {activities.slice(0, 12).map((activity) => (
              <Card 
                key={activity.name} 
                className="flex-shrink-0 w-48 overflow-hidden cursor-pointer hover:scale-105 transition-transform"
                onClick={() => {
                  // This would be passed from parent component
                  console.log('Selected activity:', activity.name);
                  // onActivitySelect?.(activity);
                }}
              >
                {activity.image ? (
                  <div 
                    className="h-24 bg-cover bg-center relative"
                    style={{
                      backgroundImage: `url(${activity.image})`
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />
                  </div>
                ) : (
                  <div className="h-24 bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white text-3xl">
                    {activity.icon}
                  </div>
                )}
                <CardContent className="p-3 bg-card text-card-foreground">
                  <h3 className="font-semibold text-sm mb-1">{activity.name}</h3>
                  <p className="text-xs text-muted-foreground mb-2">{activity.muscles}</p>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-1">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      <span className="font-medium">{activity.rating}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <Card className="mb-6 animate-fade-in">
          <CardContent className="p-4">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">24</div>
                <div className="text-xs text-muted-foreground">Workouts</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-success">1,240</div>
                <div className="text-xs text-muted-foreground">Calories</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-warning">45m</div>
                <div className="text-xs text-muted-foreground">Today</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-background/80 backdrop-blur-subtle border-t safe-bottom">
        <div className="max-w-md mx-auto px-4 py-2">
          <div className="flex justify-around">
            {[
              { id: 'training', label: 'Training', icon: Zap },
              { id: 'discover', label: 'Discover', icon: Search },
              { id: 'report', label: 'Report', icon: Target },
              { id: 'roadmap', label: 'Roadmap', icon: Calendar }
            ].map(({ id, label, icon: Icon }) => (
              <Button
                key={id}
                variant="ghost"
                size="sm"
                onClick={() => onTabChange(id)}
                className={`flex flex-col items-center space-y-1 tap-target ${
                  activeTab === id ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs">{label}</span>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;