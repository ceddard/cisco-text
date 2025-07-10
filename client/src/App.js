import React, { useState, useEffect, useRef } from 'react';
import { 
  Container, Box, Paper, TextField, Button, Typography, 
  CircularProgress, AppBar, Toolbar, Avatar,
  FormControl, Select, MenuItem, InputLabel, Chip, Fade
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ReactMarkdown from 'react-markdown';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import axios from 'axios';
import './App.css';

/**
 * Modern, elegant theme with light gray tones for a clean, pleasant visual experience
 */
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#9CA3AF', // Lighter medium gray
      dark: '#6B7280', // Medium gray
      light: '#D1D5DB', // Very light gray
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#94A3B8', // Light slate
      light: '#CBD5E1', // Very light slate
      dark: '#64748B', // Slate gray
      contrastText: '#ffffff',
    },
    background: {
      default: '#F9FAFB',
      paper: '#FFFFFF',
    },
    error: {
      main: '#EF4444',
    },
    success: {
      main: '#10B981',
    },
    info: {
      main: '#3B82F6',
    },
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
    }
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", "Roboto", sans-serif',
    h6: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    body1: {
      lineHeight: 1.7,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.02em',
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 20,
        },
        elevation1: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        },
        elevation3: {
          boxShadow: '0 10px 30px rgba(0,0,0,0.07)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '10px 20px',
          fontWeight: 600,
          boxShadow: 'none',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
          },
          transition: 'all 0.2s ease',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 16,
          }
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        }
      }
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        }
      }
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        }
      }
    },
  },
});

/**
 * Message component renders individual chat messages with ultra-modern styling
 */
const Message = ({ content, sender, timestamp, imageUrl }) => {
  const isUser = sender === 'user';
  const isSystem = sender === 'system';
  const isCurator = sender === 'curator';
  
  const getAvatarIcon = () => {
    switch(sender) {
      case 'inventor':
        return '🎨';
      case 'translator':
        return '🧠';
      case 'curator':
        return '🌙';
      case 'system':
        return '💬';
      case 'user':
        return '👤';
      default:
        return '🤖';
    }
  };
  
  const getAvatarColor = () => {
    switch(sender) {
      case 'inventor':
        return 'linear-gradient(135deg, #D1D5DB 0%, #9CA3AF 100%)';
      case 'translator':
        return 'linear-gradient(135deg, #E5E7EB 0%, #D1D5DB 100%)';
      case 'curator':
        return 'linear-gradient(135deg, #CBD5E1 0%, #9CA3AF 100%)';
      case 'system':
        return 'linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%)';
      case 'user':
        return 'linear-gradient(135deg, #9CA3AF 0%, #6B7280 100%)';
      default:
        return 'linear-gradient(135deg, #D1D5DB 0%, #9CA3AF 100%)';
    }
  };
  
  const getSenderName = () => {
    if (isUser) return 'You';
    
    switch(sender) {
      case 'inventor':
        return 'Imaginary Tool Inventor';
      case 'translator':
        return 'Unspoken Feelings Translator';
      case 'curator':
        return 'Dream Curator';
      case 'system':
        return 'System';
      default:
        return 'Assistant';
    }
  };
  
  const MessageShape = ({ children, isUser, isSystem }) => {
    return (
      <Box
        sx={{
          position: 'relative',
          '&:after': isUser ? {
            content: '""',
            position: 'absolute',
            right: '-10px',
            top: '14px',
            border: '10px solid transparent',
            borderBottomColor: isUser ? theme.palette.primary.main : 'transparent',
            borderRightColor: 'transparent',
            transform: 'rotate(-45deg)',
            display: { xs: 'none', sm: 'block' }
          } : (!isSystem ? {
            content: '""',
            position: 'absolute',
            left: '-10px',
            top: '14px',
            border: '10px solid transparent',
            borderBottomColor: 'white',
            borderLeftColor: 'transparent',
            transform: 'rotate(45deg)',
            display: { xs: 'none', sm: 'block' }
          } : {})
        }}
      >
        {children}
      </Box>
    );
  };
  
  return (
    <Fade in={true} timeout={400}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 3,
          gap: 2,
          alignItems: 'flex-start',
          px: { xs: 0, sm: 1 }
        }}
      >
        {!isUser && (
          <Avatar 
            sx={{ 
              width: 42, 
              height: 42,
              fontSize: '1.2rem',
              background: getAvatarColor(),
              boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
              border: '2px solid white',
              marginTop: '4px'
            }}
          >
            {getAvatarIcon()}
          </Avatar>
        )}
        
        <MessageShape isUser={isUser} isSystem={isSystem}>
          <Paper 
            elevation={0}
            sx={{
              p: 2.5,
              pb: 2,
              maxWidth: { xs: '80%', sm: '70%', md: '60%' },
              backgroundColor: isUser ? theme.palette.gray[400] : 
                isSystem ? theme.palette.gray[100] : theme.palette.background.paper,
              color: isUser ? 'white' : 'inherit',
              borderRadius: isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
              boxShadow: isUser ? '0 4px 16px rgba(156, 163, 175, 0.2)' : 
                isSystem ? 'none' : '0 4px 16px rgba(0, 0, 0, 0.03)',
            }}
          >
            <Box sx={{ mb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 700, 
                  color: isUser ? 'white' : 
                    isSystem ? 'text.secondary' : 
                    sender === 'inventor' ? theme.palette.secondary.main : 
                    sender === 'translator' ? theme.palette.primary.main : 
                    theme.palette.secondary.dark,
                  fontSize: '0.9rem'
                }}
              >
                {getSenderName()}
              </Typography>
              
              <Typography variant="caption" sx={{ 
                color: isUser ? 'rgba(255,255,255,0.7)' : theme.palette.text.secondary,
                fontSize: '0.75rem',
                opacity: 0.7,
                ml: 2
              }}>
                {timestamp}
              </Typography>
            </Box>
            
            <Box className="message-content" sx={{ 
              mt: 0.5
            }}>
              {isUser ? (
                <Typography variant="body1">{content}</Typography>
              ) : (
                <>
                  <ReactMarkdown>{content}</ReactMarkdown>
                  {imageUrl && isCurator && (
                    <Box 
                      sx={{ 
                        mt: 2,
                        borderRadius: '16px',
                        overflow: 'hidden',
                        boxShadow: '0 6px 20px rgba(0,0,0,0.1)',
                        position: 'relative'
                      }}
                    >
                      <img 
                        src={imageUrl} 
                        alt="Dream visualization" 
                        style={{ 
                          width: '100%', 
                          display: 'block',
                          borderRadius: '16px'
                        }} 
                      />
                      <Box 
                        sx={{ 
                          position: 'absolute', 
                          bottom: 10, 
                          right: 10,
                          backgroundColor: 'rgba(255,255,255,0.8)',
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 10,
                          fontSize: '0.75rem',
                          fontWeight: 500,
                          color: theme.palette.gray[600],
                          boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                        }}
                      >
                        Dream Visualization
                      </Box>
                    </Box>
                  )}
                </>
              )}
            </Box>
          </Paper>
        </MessageShape>
        
        {isUser && (
          <Avatar 
            sx={{ 
              width: 42, 
              height: 42,
              fontSize: '1.1rem',
              background: getAvatarColor(),
              boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
              border: '2px solid white',
              marginTop: '4px'
            }}
          >
            {getAvatarIcon()}
          </Avatar>
        )}
      </Box>
    </Fade>
  );
};

/**
 * Main Chat Application Component
 * Provides interface for user to interact with different AI assistants
 */
function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatType, setChatType] = useState('inventor');
  const [availableServices] = useState(['inventor', 'translator', 'curator']);
  const [backendConnected, setBackendConnected] = useState(true);
  
  const messagesEndRef = useRef(null);
  
  const formatTime = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        await axios.get('/', { timeout: 3000 });
        setBackendConnected(true);
      } catch (error) {
        console.warn('Backend not accessible:', error);
        setBackendConnected(false);
      }
    };
    
    checkBackendConnection();
  }, []);

  useEffect(() => {
    const welcomeMessage = {
      content: backendConnected
        ? "Hello Cisco! I'm your chat assistant. Choose a service and send your message!"
        : "⚠️ Unable to connect to backend server. Please check if the server is running at http://localhost:8000 and reload the page.",
      sender: 'system',
      timestamp: formatTime()
    };
    
    setMessages([welcomeMessage]);
  }, [backendConnected]);
  
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  /**
   * Sends user message to the backend and handles the response
   */
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = input;
    setInput('');
    
    const newMessages = [...messages, {
      content: userMessage,
      sender: 'user',
      timestamp: formatTime()
    }];
    
    setMessages(newMessages);
    setLoading(true);
    
    try {
      const response = await axios.post('/chat/message', {
        prompt: chatType,
        query: userMessage
      });
      
      setMessages([...newMessages, {
        content: response.data.response,
        sender: chatType,
        timestamp: formatTime(),
        imageUrl: response.data.image_url
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...newMessages, {
        content: "Sorry, an error occurred while processing your request.",
        sender: 'system',
        timestamp: formatTime()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ 
        height: '100vh', 
        display: 'flex', 
        flexDirection: 'column', 
        background: 'linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%)',
        overflow: 'hidden'
      }}>
        <AppBar position="static" elevation={0} sx={{ 
          background: 'rgba(249, 250, 251, 0.9)',
          backdropFilter: 'blur(10px)',
          borderBottom: `1px solid ${theme.palette.gray[200]}`
        }}>
          <Toolbar sx={{ px: { xs: 2, sm: 4 } }}>
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                flexGrow: 1, 
                fontWeight: 700, 
                background: 'linear-gradient(90deg, #6B7280 0%, #D1D5DB 100%)',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: { xs: '1.1rem', sm: '1.25rem' }
              }}
            >
              Creative AI Assistant
            </Typography>
            
            {!backendConnected && (
              <Chip 
                label="Backend Offline" 
                color="error" 
                size="small"
                sx={{ 
                  borderRadius: '10px',
                  fontWeight: 500,
                }}
              />
            )}
          </Toolbar>
        </AppBar>
        
        <Container 
          maxWidth="md" 
          sx={{ 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column', 
            py: 2,
            px: { xs: 1, sm: 2 }
          }}
        >
          <Box 
            sx={{ 
              p: { xs: 2, sm: 3 }, 
              display: 'flex', 
              justifyContent: 'center',
              mb: 2
            }}
          >
            <FormControl 
              variant="outlined" 
              sx={{ 
                width: '100%', 
                maxWidth: 550, // Increased width further
                '& .MuiOutlinedInput-root': {
                  borderRadius: '20px',
                  backgroundColor: theme.palette.gray[100],
                  boxShadow: '0 4px 12px rgba(0,0,0,0.03)',
                  transition: 'all 0.2s ease',
                  border: `1px solid ${theme.palette.gray[200]}`,
                  '&:hover': {
                    boxShadow: '0 6px 16px rgba(0,0,0,0.05)',
                    backgroundColor: theme.palette.gray[50],
                  },
                  '&.Mui-focused': {
                    boxShadow: '0 6px 20px rgba(156, 163, 175, 0.15)',
                    borderColor: theme.palette.gray[300],
                  },
                },
                '& .MuiSelect-select': {
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center', // Center the selected item
                  gap: 1.5,
                  padding: '14px 16px',
                }
              }}
            >
              <InputLabel id="chat-type-select-label" sx={{ color: theme.palette.gray[500] }}>Choose your assistant</InputLabel>
              <Select
                labelId="chat-type-select-label"
                id="chat-type-select"
                value={chatType}
                label="Choose your assistant"
                onChange={(e) => setChatType(e.target.value)}
                MenuProps={{
                  PaperProps: {
                    sx: {
                      width: 550, // Match the increased width of the dropdown
                      maxHeight: 300,
                      borderRadius: 3,
                      boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
                      backgroundColor: theme.palette.gray[50],
                      '& .MuiMenuItem-root': {
                        justifyContent: 'center', // Center menu items
                        padding: '14px 16px',
                        '&:hover': {
                          backgroundColor: theme.palette.gray[100],
                        },
                        '&.Mui-selected': {
                          backgroundColor: theme.palette.gray[200],
                        }
                      }
                    }
                  }
                }}
              >
                <MenuItem value="inventor" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, py: 2 }}>
                  <Avatar sx={{ 
                    width: 38, 
                    height: 38, 
                    background: 'linear-gradient(135deg, #D1D5DB 0%, #9CA3AF 100%)',
                    border: '2px solid white',
                    boxShadow: '0 3px 8px rgba(0,0,0,0.08)',
                    fontSize: '1.1rem' 
                  }}>🎨</Avatar>
                  <Typography sx={{ fontWeight: 600, color: theme.palette.gray[600] }}>Imaginary Tool Inventor</Typography>
                </MenuItem>
                <MenuItem value="translator" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, py: 2 }}>
                  <Avatar sx={{ 
                    width: 38, 
                    height: 38, 
                    background: 'linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%)',
                    border: '2px solid white',
                    boxShadow: '0 3px 8px rgba(0,0,0,0.08)',
                    fontSize: '1.1rem' 
                  }}>🧠</Avatar>
                  <Typography sx={{ fontWeight: 600, color: theme.palette.gray[600] }}>Unspoken Feelings Translator</Typography>
                </MenuItem>
                <MenuItem value="curator" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, py: 2 }}>
                  <Avatar sx={{ 
                    width: 38, 
                    height: 38, 
                    background: 'linear-gradient(135deg, #CBD5E1 0%, #94A3B8 100%)',
                    border: '2px solid white',
                    boxShadow: '0 3px 8px rgba(0,0,0,0.08)',
                    fontSize: '1.1rem' 
                  }}>🌙</Avatar>
                  <Typography sx={{ fontWeight: 600, color: theme.palette.gray[600] }}>Dream Curator</Typography>
                </MenuItem>
              </Select>
            </FormControl>
          </Box>
          
          <Paper 
            elevation={0}
            sx={{ 
              flexGrow: 1, 
              mx: { xs: 0, sm: 1 },
              mb: 2,
              px: { xs: 2, sm: 3 },
              py: 3,
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 4,
              bgcolor: 'rgba(249, 250, 251, 0.95)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 10px 30px rgba(0,0,0,0.05)',
              border: `1px solid ${theme.palette.gray[200]}`,
            }}
          >
            {messages.map((msg, index) => (
              <Message 
                key={index} 
                content={msg.content} 
                sender={msg.sender} 
                timestamp={msg.timestamp}
                imageUrl={msg.imageUrl}
              />
            ))}
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                <CircularProgress 
                  size={36} 
                  thickness={3}
                  sx={{
                    color: theme.palette.gray[400],
                  }}
                />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Paper>
          
          <Box 
            sx={{ 
              display: 'flex', 
              mb: 2, 
              mx: { xs: 0, sm: 1 }, 
              gap: 1.5,
              position: 'relative',
            }}
          >
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              disabled={loading || !backendConnected}
              sx={{ 
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                  backgroundColor: theme.palette.gray[100],
                  border: `1px solid ${theme.palette.gray[200]}`,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.03)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    boxShadow: '0 6px 16px rgba(0,0,0,0.05)',
                    backgroundColor: theme.palette.gray[50],
                  },
                  '&.Mui-focused': {
                    boxShadow: '0 6px 20px rgba(156, 163, 175, 0.15)',
                    borderColor: theme.palette.gray[300],
                    backgroundColor: 'white',
                  },
                }
              }}
              multiline
              maxRows={4}
            />
            <Button 
              variant="contained" 
              color="primary"
              endIcon={<SendIcon />}
              onClick={sendMessage}
              disabled={loading || !input.trim() || !backendConnected}
              sx={{ 
                minWidth: { xs: 56, sm: 110 },
                height: { xs: 56, sm: 56 },
                px: { xs: 2, sm: 3 },
                boxShadow: '0 4px 12px rgba(107, 114, 128, 0.15)',
                '&:hover': {
                  boxShadow: '0 6px 16px rgba(107, 114, 128, 0.25)',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>Send</Box>
            </Button>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
